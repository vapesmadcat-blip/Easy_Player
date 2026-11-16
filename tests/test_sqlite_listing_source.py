#!/usr/bin/env python3
"""Garante que a listagem normal consulta SQLite e não cai silenciosamente em find."""
from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EAZY = ROOT / "eazy"
INDEXER = ROOT / "eazy-index.py"


class SQLiteListingSourceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="eazy-sql-list-source-")
        self.root = Path(self.temp.name)
        source = EAZY.read_text(encoding="utf-8")
        start = source.index("# A navegação normal usa exclusivamente o índice SQLite.")
        end = source.index("\neazy_index_mark_deleted() {", start)
        self.function_file = self.root / "listing-function.sh"
        self.function_file.write_text(source[start:end], encoding="utf-8")
        self.cwd = self.root / "browse"
        self.cwd.mkdir()
        self.db = self.root / "index.sqlite3"
        self.error_file = self.root / "query-error.txt"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def shell(self, extra: str = "") -> subprocess.CompletedProcess:
        env = os.environ.copy()
        env.update({
            "EAZY_INDEXER": str(INDEXER),
            "EAZY_INDEX_DB": str(self.db),
            "EAZY_TMP_DIR": str(self.root),
            "EAZY_INDEX_QUERY_ERROR_FILE": str(self.error_file),
            "PYTHON_CMD": "python3",
            "FILTRO_ATUAL": "ambos",
            "EAZY_IGNORE": "0",
        })
        script = (
            f"source {str(self.function_file)!r}\n"
            "find() { printf 'FIND_FALLBACK_USED\\n'; return 0; }\n"
            f"cd {str(self.cwd)!r}\n"
            f"{extra}\n"
            "eazy_lista_diretorio_fonte\n"
        )
        return subprocess.run(["bash", "-c", script], env=env, capture_output=True, text=True)

    def test_reads_new_file_from_sql(self) -> None:
        target = self.cwd / "new-file.mp4"
        target.write_bytes(b"new")
        result = subprocess.run(
            ["python3", str(INDEXER), "--db", str(self.db), "--sync-dir", str(self.cwd)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

        listed = self.shell()
        self.assertEqual(listed.returncode, 0, listed.stderr)
        self.assertIn(str(target), listed.stdout)
        self.assertNotIn("FIND_FALLBACK_USED", listed.stdout)

    def test_sql_failure_is_reported_without_filesystem_fallback(self) -> None:
        other = self.root / "other"
        other.mkdir()
        subprocess.run(
            ["python3", str(INDEXER), "--db", str(self.db), "--sync-dir", str(other)],
            check=True,
            capture_output=True,
            text=True,
        )
        result = self.shell()
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("FIND_FALLBACK_USED", result.stdout)
        self.assertTrue(self.error_file.is_file())
        self.assertIn("Consulta SQLite falhou", self.error_file.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
