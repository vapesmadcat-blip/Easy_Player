#!/usr/bin/env python3
"""Regressão isolada para listas temporárias armazenadas em tabelas SQLite."""
from __future__ import annotations

import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEXER = ROOT / "eazy-index.py"


class SQLiteTempListsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="eazy-lists-test-")
        self.root = Path(self.temp.name)
        self.db = self.root / "index.sqlite3"
        self.legacy = self.root / "legacy"
        self.legacy.mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_indexer(self, *args: str, data: bytes = b"", ok: bool = True) -> subprocess.CompletedProcess:
        result = subprocess.run(
            [sys.executable, str(INDEXER), "--db", str(self.db), *args],
            input=data,
            capture_output=True,
        )
        if ok and result.returncode != 0:
            self.fail(result.stderr.decode("utf-8", "replace"))
        return result

    def test_create_append_remove_replace_clear_and_export(self) -> None:
        self.run_indexer("--list-init", "--legacy-dir", str(self.legacy))
        self.run_indexer("--list-create", "Favorites")
        path_a = "/mnt/media/ação vídeo.mkv".encode()
        path_b = b"/mnt/media/another file.mp4"
        appended = self.run_indexer("--list-append0", "Favorites", data=path_a + b"\0" + path_b + b"\0" + path_a + b"\0")
        self.assertEqual(appended.stdout, b"2\n")
        self.assertEqual(self.run_indexer("--list-count", "Favorites").stdout, b"2\n")
        self.assertEqual(self.run_indexer("--list-export", "Favorites").stdout, path_a + b"\n" + path_b + b"\n")

        removed = self.run_indexer("--list-remove0", "Favorites", data=path_a + b"\0")
        self.assertEqual(removed.stdout, b"1\n")
        self.assertEqual(self.run_indexer("--list-export", "Favorites").stdout, path_b + b"\n")

        # A restauração substitutiva preserva ordem e duplicatas como registradas.
        self.run_indexer("--list-replace0", "Favorites", data=path_b + b"\0" + path_a + b"\0" + path_b + b"\0")
        self.assertEqual(self.run_indexer("--list-export", "Favorites").stdout, path_b + b"\n" + path_a + b"\n" + path_b + b"\n")
        self.assertEqual(self.run_indexer("--list-clear", "Favorites").stdout, b"3\n")
        self.assertEqual(self.run_indexer("--list-count", "Favorites").stdout, b"0\n")

        raw = self.run_indexer("--list-menu0").stdout
        entries = raw.split(b"\0")[:-1]
        pairs = list(zip(entries[::2], entries[1::2]))
        self.assertIn((b"temp_playlist_1", b"0"), pairs)
        self.assertIn((b"Favorites", b"0"), pairs)

        with sqlite3.connect(self.db) as db:
            self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0], "ok")

    def test_reserved_identifiers_and_unknown_lists_are_rejected(self) -> None:
        self.run_indexer("--list-init", "--legacy-dir", str(self.legacy))
        rejected = self.run_indexer("--list-create", "sqlite_sequence", ok=False)
        self.assertIn(b"reservado", rejected.stderr)
        rejected = self.run_indexer("--list-append0", "not-a-list", data=b"/x\0", ok=False)
        self.assertIn("não está registrada".encode(), rejected.stderr)

    def test_legacy_files_are_not_silently_imported_or_modified(self) -> None:
        legacy_file = self.legacy / "temp_playlist_custom_ArquivoAntigo"
        original = b"/keep/this\n"
        legacy_file.write_bytes(original)
        result = self.run_indexer("--list-init", "--legacy-dir", str(self.legacy), ok=False)
        self.assertIn(b"migrate_eazy_lists.py --apply", result.stderr)
        self.assertEqual(legacy_file.read_bytes(), original)


if __name__ == "__main__":
    unittest.main(verbosity=2)
