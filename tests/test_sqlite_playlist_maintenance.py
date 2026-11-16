#!/usr/bin/env python3
"""Regressões para manutenção SQL e lookup em lote de playlists."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EAZY = ROOT / "eazy"
INDEXER = ROOT / "eazy-index.py"


class SQLitePlaylistMaintenanceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="eazy-playlist-maintenance-")
        self.root = Path(self.temp.name)
        self.db = self.root / "index.sqlite3"
        self.config = self.root / "config"
        self.config.mkdir()
        self.tmpdir = self.root / "tmp"
        self.tmpdir.mkdir()
        self.run_indexer("--list-init", "--legacy-dir", str(self.config))
        self.run_indexer("--list-create", "Favorites")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_indexer(self, *args: str, data: bytes = b"") -> subprocess.CompletedProcess:
        result = subprocess.run(
            [sys.executable, str(INDEXER), "--db", str(self.db), *args],
            input=data,
            capture_output=True,
        )
        if result.returncode:
            self.fail(result.stderr.decode("utf-8", "replace"))
        return result

    def test_sql_export_and_repair_use_nul_paths_from_table(self) -> None:
        absolute = self.config / "present video.mp4"
        relative = self.config / "relative.mp4"
        newline_path = self.config / "name\nwith-newline.mp4"
        absolute.touch(); relative.touch(); newline_path.touch()
        missing = self.config / "missing.mp4"
        paths = [str(absolute), "relative.mp4", str(newline_path), str(missing)]
        self.run_indexer("--list-append0", "Favorites", data=b"\0".join(p.encode() for p in paths) + b"\0")

        exported = self.run_indexer("--list-export0", "Favorites").stdout
        self.assertEqual(exported, b"\0".join(p.encode() for p in paths) + b"\0")

        # Um snapshot deliberadamente divergente não deve determinar a validação.
        view = self.tmpdir / "old-view.txt"
        view.write_text(str(missing) + "\n", encoding="utf-8")
        source = EAZY.read_text(encoding="utf-8")
        start = source.index("eazy_sql_list_filter_missing() {")
        end = source.index("\neazy_limpar_playlist_ausentes() {", start)
        function_file = self.root / "filter-function.sh"
        function_file.write_text(source[start:end], encoding="utf-8")
        invalidated = self.root / "invalidated.txt"
        script = f"""source {str(function_file)!r}
eazy_sql_list_indexer() {{ python3 {str(INDEXER)!r} --db {str(self.db)!r} \"$@\"; }}
eazy_sql_list_refresh_view() {{ return 0; }}
eazy_sql_list_view_path() {{ printf '%s\\n' {str(view)!r}; }}
eazy_playlist_cache_invalidate() {{ printf '%s' \"$1\" > {str(invalidated)!r}; }}
eazy_sql_list_filter_missing Favorites
"""
        env = os.environ.copy()
        env.update({"EAZY_TMP_DIR": str(self.tmpdir), "CONFIG_DIR": str(self.config)})
        repaired = subprocess.run(["bash", "-c", script], env=env, capture_output=True, text=True)
        self.assertEqual(repaired.returncode, 0, repaired.stderr)
        self.assertEqual(view.read_text(encoding="utf-8"), str(missing) + "\n")
        self.assertEqual(invalidated.read_text(encoding="utf-8"), str(view))
        actual = self.run_indexer("--list-export0", "Favorites").stdout
        expected = b"\0".join(p.encode() for p in paths[:3]) + b"\0"
        self.assertEqual(actual, expected)

    def test_lookup0_batches_a_37_item_list_and_easy_does_not_lookup_per_item(self) -> None:
        media = self.root / "media"
        media.mkdir()
        paths = []
        for i in range(37):
            path = media / f"title-{i:02}.mp4"
            path.write_bytes(b"video")
            paths.append(str(path))
        scan = subprocess.run(
            [sys.executable, str(INDEXER), "--db", str(self.db), "--sync-dir", str(media)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(scan.returncode, 0, scan.stderr)
        batch = subprocess.run(
            [sys.executable, str(INDEXER), "--db", str(self.db), "--lookup0"],
            input=b"\0".join(p.encode() for p in paths) + b"\0",
            capture_output=True,
        )
        self.assertEqual(batch.returncode, 0, batch.stderr.decode("utf-8", "replace"))
        rows = batch.stdout.decode("utf-8").splitlines()
        self.assertEqual(len(rows), 37)

        source = EAZY.read_text(encoding="utf-8")
        start = source.index("obter_lista_rapida() {")
        end = source.index('\n    if [ "${MODO_DUP:-0}" -eq 1 ]; then', start)
        renderer = source[start:end]
        self.assertIn("--lookup0", renderer)
        self.assertIn('"--list-export=$pl_sql_table"', renderer)
        self.assertNotIn('eazy_index_lookup_path "$item_res"', renderer)
        self.assertIn('pl_dir="$CONFIG_DIR"', renderer)


if __name__ == "__main__":
    unittest.main(verbosity=2)
