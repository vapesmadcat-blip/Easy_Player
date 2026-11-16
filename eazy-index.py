#!/usr/bin/env python3
"""Persistent incremental file index for eazy.

The shell UI feeds paths separated by NUL on stdin.  The index stores cheap
filesystem identity/signature fields and media metadata.  CRC32 is internal
validation data only; it is never a user-facing sort key.
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sqlite3
import stat
import subprocess
import sys
import time
import zlib
from pathlib import Path

SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
CREATE TABLE IF NOT EXISTS files (
    path TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    parent TEXT NOT NULL,
    extension TEXT NOT NULL DEFAULT '',
    kind TEXT NOT NULL DEFAULT 'other',
    mime TEXT NOT NULL DEFAULT '',
    size INTEGER NOT NULL DEFAULT 0,
    mtime_ns INTEGER NOT NULL DEFAULT 0,
    ctime_ns INTEGER NOT NULL DEFAULT 0,
    device INTEGER NOT NULL DEFAULT 0,
    inode INTEGER NOT NULL DEFAULT 0,
    crc32 TEXT NOT NULL DEFAULT '',
    duration_ms INTEGER,
    width INTEGER,
    height INTEGER,
    video_codec TEXT NOT NULL DEFAULT '',
    audio_codec TEXT NOT NULL DEFAULT '',
    bitrate INTEGER,
    indexed_at INTEGER NOT NULL DEFAULT 0,
    deleted INTEGER NOT NULL DEFAULT 0,
    deleted_at INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_files_name ON files(name COLLATE NOCASE);
CREATE INDEX IF NOT EXISTS idx_files_parent ON files(parent);
CREATE INDEX IF NOT EXISTS idx_files_size ON files(size);
CREATE INDEX IF NOT EXISTS idx_files_mtime ON files(mtime_ns);
CREATE INDEX IF NOT EXISTS idx_files_duration ON files(duration_ms);
CREATE INDEX IF NOT EXISTS idx_files_extension ON files(extension);
CREATE TABLE IF NOT EXISTS history_items (
    id INTEGER PRIMARY KEY,
    path TEXT NOT NULL UNIQUE,
    position INTEGER NOT NULL DEFAULT 0,
    played_at INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_history_position ON history_items(position);
"""

VIDEO = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".wmv", ".flv", ".m4v", ".mpg", ".mpeg", ".ts"}
AUDIO = {".mp3", ".m4a", ".wav", ".flac", ".ogg", ".opus", ".aac", ".wma"}
IMAGE = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tif", ".tiff", ".svg"}
ARCHIVE = {".zip", ".tar", ".gz", ".bz2", ".xz", ".rar", ".7z"}


def kind_for(ext: str) -> str:
    if ext in VIDEO:
        return "video"
    if ext in AUDIO:
        return "audio"
    if ext in IMAGE:
        return "image"
    if ext in ARCHIVE:
        return "archive"
    return "other"


def db_open(path: str) -> sqlite3.Connection:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=30)
    tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if not {"files", "history_items"}.issubset(tables):
        db.executescript(SCHEMA)
    else:
        # WAL é persistente; synchronous é configuração por conexão.
        db.execute("PRAGMA synchronous=NORMAL")
    # Migração silenciosa de bancos criados antes da marca de exclusão.
    cols = {row[1] for row in db.execute("PRAGMA table_info(files)")}
    if "deleted" not in cols:
        db.execute("ALTER TABLE files ADD COLUMN deleted INTEGER NOT NULL DEFAULT 0")
    if "deleted_at" not in cols:
        db.execute("ALTER TABLE files ADD COLUMN deleted_at INTEGER NOT NULL DEFAULT 0")
    db.commit()
    return db


def db_readonly(path: str) -> sqlite3.Connection:
    uri = Path(path).resolve().as_uri() + "?mode=ro"
    return sqlite3.connect(uri, uri=True, timeout=30)


def crc32_file(path: str) -> str:
    value = 0
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            value = zlib.crc32(block, value)
    return f"{value & 0xffffffff:08x}"


def media_probe(path: str):
    try:
        proc = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_format", "-show_streams", "--", path],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, timeout=20, check=False,
        )
        data = json.loads(proc.stdout or "{}")
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None
    fmt = data.get("format") or {}
    streams = data.get("streams") or []
    video = next((s for s in streams if s.get("codec_type") == "video"), {})
    audio = next((s for s in streams if s.get("codec_type") == "audio"), {})
    duration = fmt.get("duration")
    try:
        duration_ms = round(float(duration) * 1000) if duration not in (None, "N/A") else None
    except (TypeError, ValueError):
        duration_ms = None
    def integer(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
    return {
        "duration_ms": duration_ms,
        "width": integer(video.get("width")),
        "height": integer(video.get("height")),
        "video_codec": str(video.get("codec_name") or ""),
        "audio_codec": str(audio.get("codec_name") or ""),
        "bitrate": integer(fmt.get("bit_rate")),
    }


def row_for(path: str, old, st=None):
    st = st or os.stat(path, follow_symlinks=False)
    name = os.path.basename(path)
    parent = os.path.dirname(path)
    ext = os.path.splitext(name)[1].lower()
    if stat.S_ISDIR(st.st_mode):
        return {
            "path": path, "name": name, "parent": parent, "extension": "",
            "kind": "directory", "mime": "inode/directory", "size": st.st_size,
            "mtime_ns": st.st_mtime_ns, "ctime_ns": st.st_ctime_ns,
            "device": st.st_dev, "inode": st.st_ino, "crc32": "",
            "duration_ms": None, "width": None, "height": None,
            "video_codec": "", "audio_codec": "", "bitrate": None,
            "indexed_at": int(time.time()), "deleted": 0, "deleted_at": 0,
        }
    kind = kind_for(ext)
    # Assinatura rápida: não abre nem lê o conteúdo do arquivo.
    # Tamanho + mtime_ns são a regra principal; dispositivo/inode protegem
    # contra troca do arquivo mantendo o mesmo nome.
    signature = (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns)
    old_signature = None
    if old:
        old_signature = (
            old["device"], old["inode"], old["size"], old["mtime_ns"], old["ctime_ns"]
        )
    changed = old is None or signature != old_signature
    if not changed:
        return None
    mime = mimetypes.guess_type(name, strict=False)[0] or ""
    # CRC não é calculado na indexação: isso exigiria ler o arquivo inteiro.
    # A validação forte ficará restrita aos candidatos da pesquisa de duplicados.
    crc = ""
    crc_unreadable = False
    # A atualização normal é só filesystem/SQL: não inicia ffprobe por arquivo.
    # Duração/codec ficam vazios em novos/alterados; a leitura antiga fica intacta
    # enquanto a assinatura do arquivo não mudar.
    media = {"duration_ms": None, "width": None, "height": None,
             "video_codec": "", "audio_codec": "", "bitrate": None}
    return {
        "path": path, "name": name, "parent": parent, "extension": ext,
        "kind": kind, "mime": mime, "size": st.st_size,
        "mtime_ns": st.st_mtime_ns, "ctime_ns": st.st_ctime_ns,
        "device": st.st_dev, "inode": st.st_ino, "crc32": crc,
        **(media or {"duration_ms": None, "width": None, "height": None,
                     "video_codec": "", "audio_codec": "", "bitrate": None}),
        "indexed_at": int(time.time()),
        "deleted": 0,
        "deleted_at": 0,
        "_crc_unreadable": crc_unreadable,
    }


def iter_nul_paths(stream):
    """Yield NUL-separated paths without loading the whole scan into memory."""
    remainder = b""
    while True:
        chunk = stream.read(1024 * 1024)
        if not chunk:
            break
        parts = (remainder + chunk).split(b"\0")
        remainder = parts.pop()
        for raw in parts:
            if raw:
                yield raw.decode("utf-8", "surrogateescape")
    if remainder:
        yield remainder.decode("utf-8", "surrogateescape")


def write_progress(progress_file: str, processed: int, path: str) -> None:
    target = Path(progress_file)
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_name(target.name + f".{os.getpid()}.tmp")
    with temp.open("w", encoding="utf-8", errors="replace") as fh:
        fh.write(f"{processed}\t{path}\n")
    os.replace(temp, target)


def scan(db: sqlite3.Connection, paths, progress_file=None, quiet=False,
         delete_parents=None, preloaded_stats=None):
    seen = set()
    processed = changed = removed = revived = 0
    last_progress = 0.0
    preloaded_stats = preloaded_stats or {}
    select = db.execute
    old_columns = ("device", "inode", "size", "mtime_ns", "ctime_ns", "deleted",
                   "kind", "name", "path", "duration_ms")
    upsert = """
    INSERT INTO files(path,name,parent,extension,kind,mime,size,mtime_ns,ctime_ns,device,inode,crc32,
                      duration_ms,width,height,video_codec,audio_codec,bitrate,indexed_at,deleted,deleted_at)
    VALUES(:path,:name,:parent,:extension,:kind,:mime,:size,:mtime_ns,:ctime_ns,:device,:inode,:crc32,
           :duration_ms,:width,:height,:video_codec,:audio_codec,:bitrate,:indexed_at,:deleted,:deleted_at)
    ON CONFLICT(path) DO UPDATE SET
      name=excluded.name,parent=excluded.parent,extension=excluded.extension,kind=excluded.kind,
      mime=excluded.mime,size=excluded.size,mtime_ns=excluded.mtime_ns,ctime_ns=excluded.ctime_ns,
      device=excluded.device,inode=excluded.inode,crc32=excluded.crc32,duration_ms=excluded.duration_ms,
      width=excluded.width,height=excluded.height,video_codec=excluded.video_codec,
      audio_codec=excluded.audio_codec,bitrate=excluded.bitrate,indexed_at=excluded.indexed_at,
      deleted=excluded.deleted,deleted_at=excluded.deleted_at
    """
    with db:
        for raw in paths:
            path = os.path.abspath(raw)
            if path in seen:
                continue
            seen.add(path)
            processed += 1
            st = preloaded_stats.get(path)
            try:
                st = st or os.stat(path, follow_symlinks=False)
            except OSError:
                st = None
            if st is not None:
                old_row = select(
                    "SELECT device,inode,size,mtime_ns,ctime_ns,deleted,kind,name,path,duration_ms "
                    "FROM files WHERE path=?", (path,)
                ).fetchone()
                old = dict(zip(old_columns, old_row)) if old_row else None
                row = row_for(path, old, st)
                if row is not None:
                    db.execute(upsert, row)
                    changed += 1
                else:
                    row = old
                    if old and old.get("deleted"):
                        db.execute("UPDATE files SET deleted=0, deleted_at=0 WHERE path=?", (path,))
                        row["deleted"] = 0
                        revived += 1
                if not quiet and row:
                    output_kind = "d" if row["kind"] == "directory" else "f"
                    print("%s\t%s\t%s\t%s\t%s\t%s" % (
                        row["size"], row["mtime_ns"] // 1_000_000_000, output_kind,
                        row["name"], row["path"], row["duration_ms"] or ""))
            if progress_file:
                now = time.monotonic()
                if processed % 128 == 0 or now - last_progress >= 0.5:
                    write_progress(progress_file, processed, path)
                    last_progress = now

        if delete_parents is None:
            parents = sorted({os.path.dirname(p) for p in seen})
        else:
            parents = sorted({os.path.abspath(p) for p in delete_parents})
        if parents:
            now = int(time.time())
            for parent in parents:
                stale = db.execute(
                    "SELECT path,kind,deleted FROM files WHERE parent=?", (parent,)
                ).fetchall()
                for stale_path, kind, was_deleted in stale:
                    if stale_path in seen or was_deleted:
                        continue
                    try:
                        os.stat(stale_path, follow_symlinks=False)
                    except (FileNotFoundError, NotADirectoryError):
                        db.execute(
                            "UPDATE files SET deleted=1, deleted_at=? WHERE path=? AND deleted=0",
                            (now, stale_path),
                        )
                        removed += 1
                        if kind == "directory":
                            prefix = stale_path.rstrip(os.sep) + os.sep
                            cur = db.execute(
                                "UPDATE files SET deleted=1, deleted_at=? "
                                "WHERE deleted=0 AND substr(path,1,?)=?",
                                (now, len(prefix), prefix),
                            )
                            removed += cur.rowcount
                    except OSError:
                        # Permission/IO failures are not proof of deletion.
                        continue
    if progress_file:
        write_progress(progress_file, processed, "")
    if not quiet:
        sys.stdout.flush()
    return {"processed": processed, "changed": changed, "removed": removed, "revived": revived}


def sync_directory(db: sqlite3.Connection, root: str):
    root = os.path.abspath(root)
    root_st = os.stat(root, follow_symlinks=False)
    if not stat.S_ISDIR(root_st.st_mode):
        raise NotADirectoryError(root)

    paths = [root]
    stats = {root: root_st}
    current = {}
    file_count = 0
    total_bytes = 0
    with os.scandir(root) as entries:
        for entry in entries:
            path = os.path.abspath(entry.path)
            try:
                st = entry.stat(follow_symlinks=False)
            except OSError as exc:
                # Uma enumeração incompleta não pode virar marcação falsa de exclusão.
                raise OSError(f"Não foi possível conferir {path}: {exc}") from exc
            if stat.S_ISDIR(st.st_mode):
                kind = "directory"
            elif stat.S_ISREG(st.st_mode):
                kind = kind_for(os.path.splitext(entry.name)[1].lower())
                file_count += 1
                total_bytes += st.st_size
            else:
                continue
            paths.append(path)
            stats[path] = st
            current[path] = (
                st.st_size, st.st_mtime_ns, st.st_ctime_ns, st.st_dev, st.st_ino, kind
            )

    indexed_rows = db.execute(
        "SELECT path,size,mtime_ns,ctime_ns,device,inode,kind,deleted "
        "FROM files WHERE parent=?", (root,)
    ).fetchall()
    indexed = {
        row[0]: (row[1], row[2], row[3], row[4], row[5], row[6])
        for row in indexed_rows if not row[7]
    }
    indexed_files = [row for row in indexed_rows if not row[7] and row[6] != "directory"]
    indexed_dirs = [row for row in indexed_rows if not row[7] and row[6] == "directory"]
    indexed_file_count = len(indexed_files)
    indexed_bytes = sum(row[1] for row in indexed_files)
    actual_dir_count = sum(1 for row in current.values() if row[5] == "directory")

    root_row = db.execute(
        "SELECT size,mtime_ns,ctime_ns,device,inode,deleted FROM files "
        "WHERE path=? AND kind='directory'", (root,)
    ).fetchone()
    root_signature = (
        root_st.st_size, root_st.st_mtime_ns, root_st.st_ctime_ns,
        root_st.st_dev, root_st.st_ino,
    )
    root_matches = bool(root_row) and not root_row[5] and tuple(root_row[:5]) == root_signature

    # Count + bytes are the quick summary requested. Comparing the already-read
    # entries' signatures also catches same-count/same-size replacements.
    unchanged = (
        indexed_file_count == file_count
        and indexed_bytes == total_bytes
        and len(indexed_dirs) == actual_dir_count
        and indexed == current
        and root_matches
    )
    if unchanged:
        return {"processed": len(paths), "changed": 0, "removed": 0,
                "revived": 0, "files": file_count, "bytes": total_bytes}

    result = scan(
        db, paths, quiet=True, delete_parents={root}, preloaded_stats=stats
    )
    result.update({"files": file_count, "bytes": total_bytes})
    return result


LIST_FIXED = ("temp_playlist_1", "temp_playlist_2", "temp_playlist_3")
LIST_REGISTRY = "eazy_list_migrations"
LIST_RESERVED = {"files", "history_items", "history_state", LIST_REGISTRY}


def quote_identifier(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def list_registry_ensure(db: sqlite3.Connection) -> None:
    db.execute(
        f"CREATE TABLE IF NOT EXISTS {quote_identifier(LIST_REGISTRY)} ("
        "table_name TEXT PRIMARY KEY, source_file TEXT NOT NULL UNIQUE, "
        "source_sha256 TEXT NOT NULL, entry_count INTEGER NOT NULL, migrated_at TEXT NOT NULL)"
    )
    columns = {row[1] for row in db.execute(f"PRAGMA table_info({quote_identifier(LIST_REGISTRY)})")}
    required = {"table_name", "source_file", "source_sha256", "entry_count", "migrated_at"}
    if not required.issubset(columns):
        raise ValueError(f"esquema inesperado em {LIST_REGISTRY}")
    if "revision" not in columns:
        db.execute(
            f"ALTER TABLE {quote_identifier(LIST_REGISTRY)} "
            "ADD COLUMN revision INTEGER NOT NULL DEFAULT 0"
        )


def list_table_names(db: sqlite3.Connection) -> dict[str, str]:
    return {
        name.casefold(): name
        for (name,) in db.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }


def list_table_validate(db: sqlite3.Connection, table: str) -> None:
    existing = list_table_names(db).get(table.casefold())
    if existing is None:
        raise ValueError(f"a tabela de lista {table!r} não existe; execute a migração antes de usar o Easy")
    columns = [row[1] for row in db.execute(f"PRAGMA table_info({quote_identifier(existing)})")]
    if columns != ["position", "path"]:
        raise ValueError(f"a tabela de lista {existing!r} tem esquema inesperado")


def list_source_targets(source_dir: str) -> dict[str, str]:
    directory = Path(source_dir).expanduser()
    sources: dict[str, str] = {}
    for table in LIST_FIXED:
        if (directory / table).is_file():
            sources[table.casefold()] = table
    # Compatibilidade com a fila singular usada por versões antigas.
    if (directory / "temp_playlist").is_file() and "temp_playlist_1" not in sources:
        sources["temp_playlist_1"] = "temp_playlist"
    for path in directory.glob("temp_playlist_custom_*"):
        if path.is_file():
            name = path.name[len("temp_playlist_custom_"):]
            if name:
                sources[name.casefold()] = path.name
    return sources


def list_initialize(db: sqlite3.Connection, source_dir: str) -> None:
    names = list_table_names(db)
    registered = {
        row[0].casefold(): row[0]
        for row in db.execute(
            f"SELECT table_name FROM {quote_identifier(LIST_REGISTRY)}"
        )
    } if LIST_REGISTRY in names else {}
    legacy = list_source_targets(source_dir)
    unresolved = [source for target, source in legacy.items() if target not in names]
    if unresolved:
        details = ", ".join(sorted(set(legacy.values())))
        raise ValueError(
            "foram encontrados arquivos de listas antigas, mas faltam tabelas SQLite "
            f"({details}); feche o Easy e execute migrate_eazy_lists.py --apply antes de abrir as listas"
        )

    list_registry_ensure(db)
    with db:
        for name in LIST_FIXED:
            actual = list_table_names(db).get(name.casefold())
            if actual is None:
                db.execute(
                    f"CREATE TABLE {quote_identifier(name)} "
                    "(position INTEGER PRIMARY KEY, path TEXT NOT NULL)"
                )
                actual = name
            list_table_validate(db, actual)
            if actual.casefold() not in registered:
                db.execute(
                    f"INSERT INTO {quote_identifier(LIST_REGISTRY)} "
                    "(table_name,source_file,source_sha256,entry_count,migrated_at,revision) "
                    "VALUES(?,?,?,?,?,0)",
                    (actual, "@eazy-sql:" + actual, "", 0, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())),
                )
        rows = db.execute(
            f"SELECT table_name FROM {quote_identifier(LIST_REGISTRY)} ORDER BY table_name COLLATE NOCASE"
        ).fetchall()
        for (table,) in rows:
            list_table_validate(db, table)


def list_registered(db: sqlite3.Connection, table: str) -> str:
    row = db.execute(
        f"SELECT table_name FROM {quote_identifier(LIST_REGISTRY)} WHERE table_name=? COLLATE NOCASE",
        (table,),
    ).fetchone()
    if not row:
        raise ValueError(f"a lista SQLite {table!r} não está registrada")
    list_table_validate(db, row[0])
    return row[0]


def list_touch_revision(db: sqlite3.Connection, table: str) -> None:
    quoted = quote_identifier(table)
    count = db.execute(f"SELECT count(*) FROM {quoted}").fetchone()[0]
    db.execute(
        f"UPDATE {quote_identifier(LIST_REGISTRY)} "
        "SET revision=revision+1, entry_count=? WHERE table_name=? COLLATE NOCASE",
        (count, table),
    )


def list_create(db: sqlite3.Connection, table: str) -> None:
    if not table or "\x00" in table or "\n" in table or "\r" in table or "\t" in table:
        raise ValueError("o nome da lista está vazio ou contém um caractere de controle")
    if table.casefold().startswith("sqlite_") or table.casefold() in LIST_RESERVED:
        raise ValueError(f"o nome {table!r} é reservado pelo SQLite/Easy")
    list_registry_ensure(db)
    if list_table_names(db).get(table.casefold()) is not None:
        raise ValueError(f"já existe uma tabela/lista chamada {table!r}")
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with db:
        db.execute(
            f"CREATE TABLE {quote_identifier(table)} (position INTEGER PRIMARY KEY, path TEXT NOT NULL)"
        )
        db.execute(
            f"INSERT INTO {quote_identifier(LIST_REGISTRY)} "
            "(table_name,source_file,source_sha256,entry_count,migrated_at,revision) "
            "VALUES(?,?,?,?,?,0)",
            (table, "@eazy-sql:" + table, "", 0, stamp),
        )


def list_append0(db: sqlite3.Connection, table: str, raw: bytes) -> int:
    table = list_registered(db, table)
    paths = [part.decode("utf-8", "surrogateescape") for part in raw.split(b"\0") if part]
    quoted = quote_identifier(table)
    added = 0
    with db:
        existing = {row[0] for row in db.execute(f"SELECT path FROM {quoted}")}
        next_position = db.execute(f"SELECT COALESCE(MAX(position),-1)+1 FROM {quoted}").fetchone()[0]
        for path in paths:
            if path in existing:
                continue
            db.execute(f"INSERT INTO {quoted}(position,path) VALUES(?,?)", (next_position, path))
            next_position += 1
            existing.add(path)
            added += 1
        if added:
            list_touch_revision(db, table)
    return added


def list_remove0(db: sqlite3.Connection, table: str, raw: bytes) -> int:
    table = list_registered(db, table)
    paths = {part.decode("utf-8", "surrogateescape") for part in raw.split(b"\0") if part}
    if not paths:
        return 0
    quoted = quote_identifier(table)
    with db:
        rows = db.execute(f"SELECT position,path FROM {quoted} ORDER BY position").fetchall()
        kept = [path for _position, path in rows if path not in paths]
        removed = len(rows) - len(kept)
        if removed:
            db.execute(f"DELETE FROM {quoted}")
            db.executemany(
                f"INSERT INTO {quoted}(position,path) VALUES(?,?)",
                enumerate(kept),
            )
            list_touch_revision(db, table)
    return removed


def list_replace0(db: sqlite3.Connection, table: str, raw: bytes) -> int:
    table = list_registered(db, table)
    paths = [part.decode("utf-8", "surrogateescape") for part in raw.split(b"\0") if part]
    quoted = quote_identifier(table)
    with db:
        current = [row[0] for row in db.execute(f"SELECT path FROM {quoted} ORDER BY position")]
        if current != paths:
            db.execute(f"DELETE FROM {quoted}")
            db.executemany(
                f"INSERT INTO {quoted}(position,path) VALUES(?,?)",
                enumerate(paths),
            )
            list_touch_revision(db, table)
    return len(paths)


def list_clear(db: sqlite3.Connection, table: str) -> int:
    table = list_registered(db, table)
    quoted = quote_identifier(table)
    with db:
        removed = db.execute(f"SELECT count(*) FROM {quoted}").fetchone()[0]
        if removed:
            db.execute(f"DELETE FROM {quoted}")
            list_touch_revision(db, table)
    return removed


def list_menu0(db: sqlite3.Connection) -> None:
    rows = db.execute(
        f"SELECT table_name,entry_count FROM {quote_identifier(LIST_REGISTRY)} "
        "ORDER BY CASE table_name WHEN 'temp_playlist_1' THEN 1 "
        "WHEN 'temp_playlist_2' THEN 2 WHEN 'temp_playlist_3' THEN 3 ELSE 4 END, "
        "table_name COLLATE NOCASE"
    )
    for table, count in rows:
        list_table_validate(db, table)
        current = db.execute(f"SELECT count(*) FROM {quote_identifier(table)}").fetchone()[0]
        sys.stdout.buffer.write(table.encode("utf-8", "surrogateescape") + b"\0")
        sys.stdout.buffer.write(str(current).encode("ascii") + b"\0")


def list_export(db: sqlite3.Connection, table: str) -> None:
    table = list_registered(db, table)
    for (path,) in db.execute(
        f"SELECT path FROM {quote_identifier(table)} ORDER BY position"
    ):
        sys.stdout.buffer.write(path.encode("utf-8", "surrogateescape") + b"\n")


def list_export0(db: sqlite3.Connection, table: str) -> None:
    table = list_registered(db, table)
    for (path,) in db.execute(
        f"SELECT path FROM {quote_identifier(table)} ORDER BY position"
    ):
        sys.stdout.buffer.write(path.encode("utf-8", "surrogateescape") + b"\0")


def main():
    ap = argparse.ArgumentParser(description="eazy incremental SQLite index")
    ap.add_argument("--db", required=True)
    ap.add_argument("--scan0", action="store_true", help="read NUL-separated paths from stdin")
    ap.add_argument("--sync-dir", metavar="PATH", help="check and incrementally sync one directory")
    ap.add_argument("--progress-file", metavar="PATH", help="write compact scan progress state")
    ap.add_argument("--query", action="store_true", help="query indexed files")
    ap.add_argument("--root", default="", help="query root")
    ap.add_argument("--ext", default="", help="space-separated extensions or TODAS")
    ap.add_argument("--min-size", type=int, default=0)
    ap.add_argument("--max-size", type=int, default=0)
    ap.add_argument("--show-deleted", action="store_true")
    ap.add_argument("--direct", action="store_true", help="query only direct children of root")
    ap.add_argument("--include-dirs", action="store_true")
    ap.add_argument("--lookup0", action="store_true", help="lookup de caminhos separados por NUL")
    ap.add_argument("--history-sync0", action="store_true", help="migra caminhos separados por NUL em stdin para history_items")
    ap.add_argument("--history-sync-file", metavar="PATH", help="recria history_items lendo o arquivo legado linha a linha")
    ap.add_argument("--history-list", action="store_true", help="lista os caminhos do histórico SQLite")
    ap.add_argument("--history-lookup", action="store_true", help="consulta metadados dos caminhos diretamente do histórico SQLite")
    ap.add_argument("--list-init", action="store_true", help="inicializa/valida tabelas de listas sem importar arquivos")
    ap.add_argument("--legacy-dir", default="", help="pasta usada para detectar arquivos de listas ainda não migrados")
    ap.add_argument("--list-menu0", action="store_true", help="emite nome e contagem de cada lista separados por NUL")
    ap.add_argument("--list-count", metavar="TABLE", help="conta os itens de uma lista")
    ap.add_argument("--list-export", metavar="TABLE", help="emite os caminhos da lista, em ordem, uma linha por item")
    ap.add_argument("--list-export0", metavar="TABLE", help="emite os caminhos da lista em ordem, separados por NUL")
    ap.add_argument("--list-create", metavar="TABLE", help="cria uma lista temporária SQL vazia")
    ap.add_argument("--list-append0", metavar="TABLE", help="anexa caminhos NUL-delimitados sem duplicar caminhos existentes")
    ap.add_argument("--list-remove0", metavar="TABLE", help="remove todos os caminhos NUL-delimitados da lista")
    ap.add_argument("--list-replace0", metavar="TABLE", help="substitui a lista pelo fluxo NUL-delimitado, preservando ordem e duplicatas")
    ap.add_argument("--list-clear", metavar="TABLE", help="esvazia uma lista sem remover sua tabela")
    ap.add_argument("--init", action="store_true")
    args = ap.parse_args()
    write_mode = bool(
        args.init or args.scan0 or args.sync_dir or args.history_sync0 or args.history_sync_file
        or args.list_init or args.list_create or args.list_append0 or args.list_remove0
        or args.list_replace0 or args.list_clear
    )
    if write_mode:
        db = db_open(args.db)
    else:
        if not Path(args.db).is_file():
            return 2 if (args.query or args.list_menu0 or args.list_count or args.list_export or args.list_export0) else 0
        db = db_readonly(args.db)
    if args.init:
        db.close()
        return 0
    if args.list_init:
        try:
            list_initialize(db, args.legacy_dir)
        except (sqlite3.DatabaseError, OSError, ValueError) as exc:
            print(f"Erro ao inicializar listas SQLite: {exc}", file=sys.stderr)
            db.close()
            return 1
        db.close()
        return 0
    if args.list_create:
        try:
            list_create(db, args.list_create)
        except (sqlite3.DatabaseError, ValueError) as exc:
            print(f"Erro ao criar lista SQLite: {exc}", file=sys.stderr)
            db.close()
            return 1
        db.close()
        return 0
    if args.list_append0 or args.list_remove0 or args.list_replace0:
        table = args.list_append0 or args.list_remove0 or args.list_replace0
        raw = sys.stdin.buffer.read()
        try:
            if args.list_append0:
                changed = list_append0(db, table, raw)
            elif args.list_remove0:
                changed = list_remove0(db, table, raw)
            else:
                changed = list_replace0(db, table, raw)
        except (sqlite3.DatabaseError, ValueError) as exc:
            print(f"Erro ao alterar lista SQLite: {exc}", file=sys.stderr)
            db.close()
            return 1
        print(changed)
        db.close()
        return 0
    if args.list_clear:
        try:
            changed = list_clear(db, args.list_clear)
        except (sqlite3.DatabaseError, ValueError) as exc:
            print(f"Erro ao limpar lista SQLite: {exc}", file=sys.stderr)
            db.close()
            return 1
        print(changed)
        db.close()
        return 0
    if args.list_menu0:
        try:
            list_menu0(db)
        except (sqlite3.DatabaseError, ValueError) as exc:
            print(f"Erro ao listar tabelas SQLite: {exc}", file=sys.stderr)
            db.close()
            return 1
        db.close()
        return 0
    if args.list_count or args.list_export or args.list_export0:
        table = args.list_count or args.list_export or args.list_export0
        try:
            table = list_registered(db, table)
            if args.list_count:
                print(db.execute(f"SELECT count(*) FROM {quote_identifier(table)}").fetchone()[0])
            elif args.list_export0:
                list_export0(db, table)
            else:
                list_export(db, table)
        except (sqlite3.DatabaseError, ValueError) as exc:
            print(f"Erro ao consultar lista SQLite: {exc}", file=sys.stderr)
            db.close()
            return 1
        db.close()
        return 0
    if args.sync_dir:
        try:
            result = sync_directory(db, args.sync_dir)
        except OSError as exc:
            print(f"Erro ao sincronizar pasta: {exc}", file=sys.stderr)
            db.close()
            return 1
        print("SYNC\t{changed}\t{removed}\t{revived}\t{files}\t{bytes}".format(**result))
        db.close()
        return 0
    if args.history_sync0 or args.history_sync_file:
        if args.history_sync_file:
            # O histórico legado é texto UTF-8/bytes surrogate-escaped, uma entrada por linha.
            # Ler diretamente evita conversões newline/NUL sujeitas a quoting incorreto.
            raw = Path(args.history_sync_file).read_bytes()
            entries = raw.split(b"\n")
            if entries and entries[-1] == b"":
                entries.pop()
            paths = [entry.decode("utf-8", "surrogateescape") for entry in entries if entry]
        else:
            paths = [p.decode("utf-8", "surrogateescape") for p in sys.stdin.buffer.read().split(b"\0") if p]
        # O histórico é único por caminho; preserve a primeira ocorrência (mais recente) se
        # um arquivo legado antigo contiver duplicatas, respeitando a restrição SQL UNIQUE.
        unique_paths = []
        seen_paths = set()
        for path in paths:
            if path not in seen_paths:
                seen_paths.add(path)
                unique_paths.append(path)
        now = int(time.time())
        with db:
            db.execute("CREATE TABLE IF NOT EXISTS history_state (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
            db.execute("DELETE FROM history_items")
            db.executemany(
                "INSERT INTO history_items(path, position, played_at) VALUES (?, ?, ?)",
                [(path, pos, now - pos) for pos, path in enumerate(unique_paths)],
            )
            db.execute("INSERT OR REPLACE INTO history_state(key, value) VALUES ('migrated', '1')")
        db.close()
        return 0
    if args.history_list:
        for (path,) in db.execute("SELECT path FROM history_items ORDER BY position ASC, id ASC"):
            print(path)
        db.close()
        return 0
    if args.history_lookup:
        rows = db.execute(
            "SELECT h.path, f.size, f.mtime_ns, f.kind, f.name, f.duration_ms, f.extension, f.deleted "
            "FROM history_items AS h LEFT JOIN files AS f ON f.path=h.path "
            "ORDER BY h.position ASC, h.id ASC"
        ).fetchall()
        for path, size, mtime_ns, kind, name, duration_ms, ext, deleted in rows:
            size = size or 0
            mtime_ns = mtime_ns or 0
            kind = kind or "other"
            name = name or os.path.basename(path)
            ext = ext or os.path.splitext(name)[1].lower()
            output_kind = "d" if kind == "directory" else "f"
            if deleted:
                output_kind = "x" if output_kind == "f" else "X"
            print(f"{size}\t{mtime_ns // 1_000_000_000}\t{output_kind}\t{name}\t{path}\t{duration_ms or ''}\t{ext}")
        db.close()
        return 0
    if args.lookup0:
        paths = [p.decode("utf-8", "surrogateescape") for p in sys.stdin.buffer.read().split(b"\0") if p]
        # Mantém margem sob o limite de variáveis SQL, inclusive em listas longas.
        for start in range(0, len(paths), 500):
            batch = paths[start:start + 500]
            marks = ",".join("?" for _ in batch)
            rows = db.execute(
                f"SELECT size,mtime_ns,kind,name,path,duration_ms,extension,deleted FROM files WHERE path IN ({marks})",
                batch,
            ).fetchall()
            for size, mtime_ns, kind, name, path, duration_ms, ext, deleted in rows:
                output_kind = "d" if kind == "directory" else "f"
                if deleted:
                    output_kind = "x" if output_kind == "f" else "X"
                print(f"{size}\t{mtime_ns // 1_000_000_000}\t{output_kind}\t{name}\t{path}\t{duration_ms or ''}\t{ext}")
        db.close()
        return 0
    if args.scan0:
        scan(db, iter_nul_paths(sys.stdin.buffer), progress_file=args.progress_file,
             quiet=bool(args.progress_file))
    elif args.query:
        root = os.path.abspath(args.root or os.getcwd()).rstrip(os.sep) or os.sep
        indexed = db.execute("SELECT count(*) FROM files WHERE path=? OR path LIKE ?", (root, root + os.sep + "%")).fetchone()[0]
        if indexed == 0:
            db.close()
            return 2
        exts = {x.lower().lstrip(".") for x in args.ext.split() if x and x.upper() != "TODAS"}
        sql = "SELECT size, mtime_ns, kind, name, path, duration_ms, extension, deleted FROM files WHERE "
        if args.include_dirs:
            sql += "1=1"
        else:
            sql += "kind != 'directory'"
        if args.direct:
            sql += " AND parent=?"
            params = [root]
        else:
            sql += " AND (path=? OR path LIKE ?)"
            params = [root, root + os.sep + "%"]
        if not args.show_deleted:
            sql += " AND deleted=0"
        if exts:
            marks = ",".join("?" for _ in exts)
            sql += f" AND (kind='directory' OR lower(ltrim(extension, '.')) IN ({marks}))"
            params.extend(sorted(exts))
        if args.min_size:
            sql += " AND size > ?"
            params.append(args.min_size)
        if args.max_size:
            sql += " AND size < ?"
            params.append(args.max_size)
        # Diretórios ficam sempre no topo. Para diretórios, `size` é somente
        # o st_size da própria entrada; nunca somamos a árvore.
        if args.ext and args.ext.upper() != "TODAS":
            sql += " ORDER BY CASE WHEN kind='directory' THEN 0 ELSE 1 END, "
        else:
            sql += " ORDER BY CASE WHEN kind='directory' THEN 0 ELSE 1 END, "
        if args.max_size or args.min_size:
            sql += "size DESC, "
        sql += "name COLLATE NOCASE"
        for size, mtime_ns, kind, name, path, duration_ms, _ext, deleted in db.execute(sql, params):
            output_kind = "d" if kind == "directory" else "f"
            if deleted:
                output_kind = "x" if output_kind == "f" else "X"
            print(f"{size}\t{mtime_ns // 1_000_000_000}\t{output_kind}\t{name}\t{path}\t{duration_ms or ''}")
    db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
