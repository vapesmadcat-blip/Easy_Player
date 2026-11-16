#!/usr/bin/env python3
"""Regressão isolada para sincronização de pastas novas e listagem do pai."""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEXER = ROOT / "eazy-index.py"


class DirectorySyncTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="eazy-dir-sync-")
        self.root = Path(self.temp.name)
        self.parent = self.root / "pai"
        self.parent.mkdir()
        self.db = self.root / "index.sqlite3"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_indexer(self, *args: str, data: bytes = b"") -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(INDEXER), "--db", str(self.db), *args],
            input=data,
            capture_output=True,
            text=False,
        )

    def query(self, path: Path) -> str:
        result = self.run_indexer(
            "--query", "--root", str(path), "--direct", "--include-dirs", "--ext", "TODAS"
        )
        self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", "replace"))
        return result.stdout.decode("utf-8", "surrogateescape")

    def test_new_directory_and_new_file_are_visible_after_sync(self) -> None:
        result = self.run_indexer("--sync-dir", str(self.parent))
        self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", "replace"))

        new_dir = self.parent / "pasta nova"
        new_dir.mkdir()
        new_file = new_dir / "arquivo_novo.mp4"
        new_file.write_bytes(b"conteudo de teste")

        # Simula o Easy iniciado dentro da pasta recém-criada.
        result = self.run_indexer("--sync-dir", str(new_dir))
        self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", "replace"))
        self.assertIn(str(new_file), self.query(new_dir))

        # Simula sair da pasta: a sincronização do pai deve registrar a subpasta.
        result = self.run_indexer("--sync-dir", str(self.parent))
        self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", "replace"))
        parent_listing = self.query(self.parent)
        self.assertIn(str(new_dir), parent_listing)
        self.assertIn("pasta nova", parent_listing)

        # A consulta com o filtro de vídeo também deve conter o arquivo.
        filtered = self.run_indexer(
            "--query", "--root", str(new_dir), "--direct", "--include-dirs", "--ext", "mp4 mkv"
        )
        self.assertEqual(filtered.returncode, 0, filtered.stderr.decode("utf-8", "replace"))
        self.assertIn(str(new_file), filtered.stdout.decode("utf-8", "surrogateescape"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
