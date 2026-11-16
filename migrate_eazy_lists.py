#!/usr/bin/env python3
"""Migra as filas e listas temporárias do Eazy para tabelas SQLite separadas.

Por padrão, apenas mostra uma prévia. Use --apply para gravar. Os arquivos-fonte
nunca são apagados. Cada tabela de lista tem as colunas position e path.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REGISTRY = "eazy_list_migrations"
RESERVED_TABLES = {"files", "history_items", "history_state", REGISTRY.casefold()}
FIXED_FILES = ("temp_playlist_1", "temp_playlist_2", "temp_playlist_3")


@dataclass
class ListSource:
    source: Path
    table: str
    raw: bytes
    paths: list[str]
    digest: str
    action: str = "create"
    note: str = ""


def quote_identifier(name: str) -> str:
    """Quote a SQLite identifier safely, including punctuation in list names."""
    return '"' + name.replace('"', '""') + '"'


def default_source_dir() -> Path:
    xdg = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return xdg / "eazy"


def read_entries(path: Path) -> tuple[bytes, list[str]]:
    raw = path.read_bytes()
    if not raw:
        return raw, []
    lines = raw.split(b"\n")
    if raw.endswith(b"\n"):
        lines.pop()  # não cria uma entrada extra só por causa do newline final
    entries: list[str] = []
    for number, line in enumerate(lines, 1):
        if line.endswith(b"\r"):
            line = line[:-1]  # aceita arquivos CRLF sem incluir CR no caminho
        try:
            entries.append(line.decode("utf-8", "strict"))
        except UnicodeDecodeError as exc:
            raise ValueError(f"{path.name}, linha {number}: não é UTF-8 válido ({exc})") from exc
    return raw, entries


def discover_sources(source_dir: Path) -> list[tuple[Path, str]]:
    sources: list[tuple[Path, str]] = []
    # A fila singular existia antes da separação em três filas. O Easy antigo
    # só a movia para Fila 1 quando temp_playlist_1 ainda não existia.
    legacy_single = source_dir / "temp_playlist"
    if legacy_single.is_file() and not (source_dir / "temp_playlist_1").is_file():
        sources.append((legacy_single, "temp_playlist_1"))
    for filename in FIXED_FILES:
        path = source_dir / filename
        if path.is_file():
            sources.append((path, filename))
    for path in sorted(source_dir.glob("temp_playlist_custom_*"), key=lambda item: item.name):
        if path.is_file():
            # A tabela personalizada recebe exatamente o nome escolhido na lista.
            table_name = path.name[len("temp_playlist_custom_"):]
            sources.append((path, table_name))
    return sources


def validate_names(sources: list[tuple[Path, str]]) -> None:
    seen: dict[str, str] = {}
    for path, name in sources:
        if not name:
            raise ValueError(f"{path.name}: nome de tabela vazio")
        if "\x00" in name:
            raise ValueError(f"{path.name}: nome de tabela contém NUL")
        try:
            name.encode("utf-8", "strict")
        except UnicodeEncodeError as exc:
            raise ValueError(f"{path.name}: nome da lista não é UTF-8 válido") from exc
        if name.casefold().startswith("sqlite_"):
            raise ValueError(f"{path.name}: prefixo sqlite_ é reservado pelo SQLite")
        key = name.casefold()
        if path.name.startswith("temp_playlist_custom_") and key in {item.casefold() for item in FIXED_FILES}:
            raise ValueError(f"{path.name}: nome de tabela reservado para uma fila fixa")
        if key in RESERVED_TABLES:
            raise ValueError(f"{path.name}: {name!r} é nome reservado pelo Easy/migrador")
        if key in seen:
            raise ValueError(
                f"colisão de nomes de tabela: {seen[key]} e {path.name} resultam em {name!r}"
            )
        seen[key] = path.name


def read_database_state(db_path: Path) -> tuple[set[str], dict[str, tuple[str, str, int]], Optional[str]]:
    if not db_path.is_file():
        return set(), {}, None
    uri = db_path.resolve().as_uri() + "?mode=ro"
    con = sqlite3.connect(uri, uri=True, timeout=10)
    try:
        table_names = {
            row[0]
            for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        registry: dict[str, tuple[str, str, int]] = {}
        if REGISTRY in table_names:
            columns = {row[1] for row in con.execute(f"PRAGMA table_info({quote_identifier(REGISTRY)})")}
            required = {"table_name", "source_file", "source_sha256", "entry_count"}
            if not required.issubset(columns):
                raise ValueError(f"a tabela interna {REGISTRY} tem um esquema inesperado")
            for table_name, source_file, digest, entry_count in con.execute(
                f"SELECT table_name, source_file, source_sha256, entry_count FROM {quote_identifier(REGISTRY)}"
            ):
                registry[table_name.casefold()] = (source_file, digest, entry_count)
        return table_names, registry, None
    finally:
        con.close()


def table_matches(con: sqlite3.Connection, table: str, paths: list[str]) -> bool:
    quoted = quote_identifier(table)
    try:
        columns = [row[1] for row in con.execute(f"PRAGMA table_info({quoted})")]
        if columns != ["position", "path"]:
            return False
        rows = con.execute(f"SELECT position, path FROM {quoted} ORDER BY position").fetchall()
        return rows == list(enumerate(paths))
    except sqlite3.DatabaseError:
        return False


def build_plan(
    sources: list[ListSource],
    db_path: Path,
    replace: bool,
) -> tuple[list[ListSource], list[str]]:
    errors: list[str] = []
    try:
        existing_tables, registry, _ = read_database_state(db_path)
    except (sqlite3.DatabaseError, ValueError) as exc:
        return sources, [str(exc)]
    existing_casefold = {name.casefold(): name for name in existing_tables}
    if db_path.is_file():
        con = sqlite3.connect(db_path.resolve().as_uri() + "?mode=ro", uri=True, timeout=10)
    else:
        con = None
    try:
        for item in sources:
            target_key = item.table.casefold()
            existing_name = existing_casefold.get(target_key)
            record = registry.get(target_key)
            if record:
                registered_source, old_digest, _count = record
                if registered_source != item.source.name:
                    errors.append(
                        f"tabela {item.table!r} já está registrada para {registered_source!r}, "
                        f"não para {item.source.name!r}"
                    )
                    item.action = "conflict"
                elif (
                    old_digest == item.digest
                    and existing_name
                    and con is not None
                    and table_matches(con, existing_name, item.paths)
                ):
                    item.action = "skip"
                    item.note = "já migrada; arquivo e conteúdo real da tabela conferem"
                elif replace:
                    item.action = "replace" if existing_name else "create"
                    item.note = "substituir tabela pelo conteúdo atual do arquivo" if existing_name else "recriar tabela ausente"
                else:
                    item.action = "conflict"
                    errors.append(
                        f"{item.source.name}: o registro existe, mas o arquivo mudou, a tabela sumiu "
                        "ou o conteúdo SQL diverge do arquivo; revise e use --apply --replace "
                        "somente se deseja substituir"
                    )
            elif existing_name:
                if con is not None and table_matches(con, existing_name, item.paths):
                    item.action = "register"
                    item.note = "a tabela já tem o conteúdo exato; registrar a migração sem reescrevê-la"
                elif replace:
                    item.action = "replace"
                    item.note = "substituir tabela existente pelo conteúdo do arquivo"
                else:
                    item.action = "conflict"
                    errors.append(
                        f"a tabela {existing_name!r} já existe e não corresponde ao arquivo "
                        f"{item.source.name}; nada será sobrescrito. Revise ou use --apply --replace"
                    )
            else:
                item.action = "create"
                item.note = "criar tabela"
    finally:
        if con is not None:
            con.close()
    return sources, errors


def make_backup(db_path: Path) -> Optional[Path]:
    if not db_path.is_file():
        return None
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backup = db_path.with_name(db_path.name + ".backup-list-migration-" + stamp)
    src = sqlite3.connect(str(db_path), timeout=30)
    dst = sqlite3.connect(str(backup))
    try:
        src.backup(dst)
    finally:
        dst.close()
        src.close()
    return backup


def apply_plan(sources: list[ListSource], db_path: Path) -> int:
    changing = [item for item in sources if item.action != "skip"]
    if not changing:
        return 0
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(db_path), timeout=30)
    try:
        con.execute("BEGIN IMMEDIATE")
        con.execute(
            f"CREATE TABLE IF NOT EXISTS {quote_identifier(REGISTRY)} ("
            "table_name TEXT PRIMARY KEY, source_file TEXT NOT NULL UNIQUE, "
            "source_sha256 TEXT NOT NULL, entry_count INTEGER NOT NULL, migrated_at TEXT NOT NULL)"
        )
        stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        for item in changing:
            quoted = quote_identifier(item.table)
            exists = con.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? COLLATE NOCASE",
                (item.table,),
            ).fetchone()
            if exists and item.action in ("replace",):
                con.execute(f"DROP TABLE {quoted}")
                exists = None
            if not exists:
                con.execute(
                    f"CREATE TABLE {quoted} (position INTEGER PRIMARY KEY, path TEXT NOT NULL)"
                )
                con.executemany(
                    f"INSERT INTO {quoted}(position,path) VALUES(?,?)",
                    enumerate(item.paths),
                )
            elif item.action == "register" and not table_matches(con, item.table, item.paths):
                raise RuntimeError(f"a tabela {item.table!r} mudou durante a migração; operação cancelada")
            con.execute(
                f"INSERT INTO {quote_identifier(REGISTRY)} "
                "(table_name,source_file,source_sha256,entry_count,migrated_at) VALUES(?,?,?,?,?) "
                "ON CONFLICT(table_name) DO UPDATE SET source_file=excluded.source_file, "
                "source_sha256=excluded.source_sha256, entry_count=excluded.entry_count, migrated_at=excluded.migrated_at",
                (item.table, item.source.name, item.digest, len(item.paths), stamp),
            )
        con.commit()
        integrity = con.execute("PRAGMA integrity_check").fetchone()
        if not integrity or integrity[0] != "ok":
            raise RuntimeError(f"integrity_check após a migração falhou: {integrity}")
        return len(changing)
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Migra filas/listas temporárias do Eazy para tabelas SQLite individuais."
    )
    parser.add_argument(
        "--source-dir", type=Path, default=default_source_dir(),
        help="pasta dos arquivos temp_playlist_* (padrão: ~/.config/eazy)",
    )
    parser.add_argument(
        "--db", type=Path, default=None,
        help="banco SQLite de destino (padrão: <source-dir>/eazy-index.sqlite3)",
    )
    parser.add_argument("--apply", action="store_true", help="grava a migração; sem esta opção só mostra a prévia")
    parser.add_argument("--replace", action="store_true", help="com --apply, substitui tabela existente/alterada a partir do arquivo")
    args = parser.parse_args(argv)
    if args.replace and not args.apply:
        parser.error("--replace exige também --apply")
    source_dir = args.source_dir.expanduser().resolve()
    db_path = (args.db or (source_dir / "eazy-index.sqlite3")).expanduser().resolve()
    if not source_dir.is_dir():
        print(f"Erro: pasta de origem não encontrada: {source_dir}", file=sys.stderr)
        return 2
    try:
        found = discover_sources(source_dir)
        validate_names(found)
        sources: list[ListSource] = []
        for path, table in found:
            raw, paths = read_entries(path)
            sources.append(ListSource(path, table, raw, paths, hashlib.sha256(raw).hexdigest()))
        sources, errors = build_plan(sources, db_path, args.replace)
    except (OSError, ValueError, sqlite3.DatabaseError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 2
    if not sources:
        print(f"Nenhum arquivo temp_playlist_1/2/3 ou temp_playlist_custom_* encontrado em {source_dir}")
        return 0
    mode = "APLICAR" if args.apply else "PRÉVIA (nenhuma alteração será feita)"
    print(f"Modo: {mode}\nOrigem: {source_dir}\nBanco:  {db_path}\n")
    for item in sources:
        print(
            f"{item.source.name} -> tabela {item.table!r}: "
            f"{len(item.paths)} entradas; {item.action}; {item.note}"
        )
    if errors:
        print("\nConflitos; nenhuma migração aplicada:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 2
    if not args.apply:
        print("\nPara gravar, feche o Easy e execute novamente com --apply."
              " Os arquivos originais serão preservados.")
        return 0
    backup: Optional[Path] = None
    try:
        if any(item.action != "skip" for item in sources):
            backup = make_backup(db_path)
        count = apply_plan(sources, db_path)
    except (OSError, sqlite3.DatabaseError, RuntimeError) as exc:
        print(f"Erro durante a migração: {exc}", file=sys.stderr)
        if backup:
            print(f"Backup disponível: {backup}", file=sys.stderr)
        return 1
    if count == 0:
        print("Nada a alterar: todas as listas já estão migradas e registradas.")
    elif backup:
        print(f"Backup do banco: {backup}")
    else:
        print("Banco criado agora; não havia banco anterior para copiar.")
    if count:
        print(f"Concluído: {count} lista(s) migrada(s)/registrada(s). Arquivos originais não foram apagados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
