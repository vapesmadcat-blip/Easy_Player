#!/usr/bin/env python3
"""Regression test for rebuilding eazy's SQLite history from the legacy file."""
from __future__ import annotations

import hashlib
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEXER = ROOT / "eazy-index.py"
EAZY = (ROOT / "eazy").read_text(encoding="utf-8")


def run(*args: str, input_bytes: bytes | None = None) -> bytes:
    proc = subprocess.run(
        [sys.executable, str(INDEXER), *args],
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return proc.stdout


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="eazy-history-test-") as tmp:
        base = Path(tmp)
        db_path = base / "eazy-index.sqlite3"
        source = base / "history"
        expected = [
            "/mnt/c/Users/Jim/Filmes/Noite N 0.mp4",
            "/home/jim/Vídeos/ação 01.mkv",
            "/mnt/d/Series/Temporada 2/Episódio 03.mp4",
            "/home/jim/Downloads/um arquivo com espaços.mp4",
        ]
        source_bytes = ("\n".join(expected) + "\n").encode("utf-8")
        source.write_bytes(source_bytes)
        source_hash = hashlib.sha256(source.read_bytes()).hexdigest()

        run("--db", str(db_path), "--init")
        # Modela um banco já usado: outra tabela deve permanecer intacta.
        with sqlite3.connect(db_path) as db:
            db.execute("INSERT INTO files(path,name,parent) VALUES(?,?,?)", ("/sentinel", "sentinel", "/"))
            db.execute(
                "INSERT INTO files(path,name,parent,mtime_ns) VALUES(?,?,?,?)",
                (expected[0], Path(expected[0]).name, str(Path(expected[0]).parent), 1673047376000000000),
            )
            db.execute("CREATE TABLE IF NOT EXISTS history_state (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
            db.execute("INSERT OR REPLACE INTO history_state VALUES('migrated','1')")
            db.execute("INSERT INTO history_items(path,position,played_at) VALUES(?,?,?)", ("CORRUPTED", 0, 1))
            db.execute("DROP TABLE history_items")
            db.execute("DROP TABLE history_state")

        # Este é o mesmo modo usado na migração de primeira entrada pelo programa.
        run("--db", str(db_path), "--history-sync-file", str(source))
        actual = run("--db", str(db_path), "--history-list").decode("utf-8").splitlines()
        assert actual == expected, f"history_items diverge do arquivo original: {actual!r} != {expected!r}"
        assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash, "o arquivo legado foi alterado"

        with sqlite3.connect(db_path) as db:
            rows = db.execute("SELECT path,position FROM history_items ORDER BY position,id").fetchall()
            marker = db.execute("SELECT value FROM history_state WHERE key='migrated'").fetchone()
            sentinel = db.execute("SELECT name FROM files WHERE path='/sentinel'").fetchone()
            assert rows == [(path, i) for i, path in enumerate(expected)], rows
            assert marker == ("1",), marker
            assert sentinel == ("sentinel",), sentinel

        looked_up = run("--db", str(db_path), "--history-lookup").decode("utf-8").splitlines()
        assert len(looked_up) == len(expected), looked_up
        assert [row.split("\t")[4] for row in looked_up] == expected, looked_up
        assert looked_up[0].split("\t")[1] == "1673047376", looked_up[0]

        lookup0 = run("--db", str(db_path), "--lookup0", input_bytes=expected[0].encode() + b"\0").decode().splitlines()
        assert lookup0[0].split("\t")[1] == "1673047376", lookup0

        scanned = base / "scan N 0.mp4"
        scanned.write_bytes(b"test")
        scan_rows = run("--db", str(db_path), "--scan0", input_bytes=str(scanned).encode() + b"\0").decode().splitlines()
        assert scan_rows and scan_rows[0].split("\t")[1].isdigit(), scan_rows
        query_rows = run("--db", str(db_path), "--query", "--root", str(base), "--ext", "TODAS").decode().splitlines()
        assert query_rows and query_rows[0].split("\t")[1].isdigit(), query_rows

        # O importador NUL legado continua funcional, sem confundir a letra N com o byte NUL.
        legacy_db = base / "legacy.sqlite3"
        nul_payload = b"/tmp/N 0\0/tmp/outro\0"
        run("--db", str(legacy_db), "--history-sync0", input_bytes=nul_payload)
        legacy_rows = run("--db", str(legacy_db), "--history-list").decode().splitlines()
        assert legacy_rows == ["/tmp/N 0", "/tmp/outro"], legacy_rows

    # Ambos os caminhos de interface passam pela barreira comum de migração.
    assert 'elif ! eazy_history_migrate_on_entry; then' in EAZY, "Ctrl+G não bloqueia na migração inicial"
    ctrlp_hist = EAZY.find('hist)\n            eazy_history_migrate_on_entry || return 1')
    assert ctrlp_hist >= 0, "Ctrl+P não chama a mesma migração ao abrir Histórico"
    assert '--history-sync-file "$HISTORY_FILE"' in EAZY, "migração não lê o arquivo original diretamente"
    assert '--history-lookup' in EAZY, "tela do histórico não consulta diretamente o SQLite"
    assert "O Easy vai recriar history_items lendo cada linha do arquivo original:" in EAZY, "aviso de migração não explica a origem dos dados"
    assert "O arquivo será mantido intacto; não haverá conversão nem substituição de caracteres." in EAZY, "aviso não garante preservação do arquivo original"

    print("PASS: rebuild SQLite igual ao arquivo original; ordem, marcador e arquivo preservados")
    print("PASS: consulta da interface vem do SQLite; Ctrl+G e Ctrl+P passam pela migração comum")
    print("PASS: timestamps do SQLite são emitidos como segundos inteiros para o shell")
    print("PASS: caminhos com letras, dígitos, espaços e acentos são preservados")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
