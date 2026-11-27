#!/usr/bin/env python3
"""Regression coverage for byte totals when selecting a directory with Space."""
import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEXER = ROOT / "eazy-index.py"


class SelectedDirectorySizeTests(unittest.TestCase):
    def run_indexer(self, db: Path, *args: str, data: bytes | None = None) -> str:
        result = subprocess.run(
            ["python3", str(INDEXER), "--db", str(db), *args],
            input=data,
            capture_output=True,
            check=True,
        )
        return result.stdout.decode().strip()

    def test_directory_selection_reports_recursive_file_bytes_not_directory_metadata(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "current"
            folder = root / "selected folder"
            nested = folder / "nested"
            nested.mkdir(parents=True)
            file_a = folder / "a.bin"
            file_b = nested / "b.bin"
            file_a.write_bytes(b"a" * 7)
            file_b.write_bytes(b"b" * 13)
            expected_bytes = file_a.stat().st_size + file_b.stat().st_size
            db = base / "index.sqlite3"
            self.run_indexer(db, "--init")

            # Seed one existing row with an obsolete size: marking the directory
            # must refresh it from the current filesystem metadata.
            with sqlite3.connect(db) as connection:
                connection.execute(
                    "INSERT INTO files(path,name,parent,kind,size,selected) VALUES(?,?,?,?,?,0)",
                    (str(file_a), file_a.name, str(file_a.parent), "other", 999_999),
                )

            descendants = b"\0".join(str(path).encode() for path in (file_a, file_b)) + b"\0"
            toggled = self.run_indexer(
                db,
                "--selection-toggle-directory-ui",
                str(folder),
                "--selection-root",
                str(root),
                data=descendants,
            )
            values = tuple(map(int, toggled.split("\t")))
            self.assertEqual(len(values), 7)
            state, global_count, global_bytes, global_dirs, local_count, local_bytes, local_dirs = values
            self.assertEqual(state, 1)
            self.assertEqual((global_count, global_bytes, global_dirs), (0, 0, 0))
            self.assertEqual((local_count, local_bytes, local_dirs), (1, expected_bytes, 1))

            # Once promoted globally, the total remains the payload size: it
            # must not include directory inode sizes or count the folder twice.
            self.run_indexer(db, "--selection-promote", "--selection-root", str(root))
            stats = self.run_indexer(db, "--selection-ui-stats", "--selection-root", str(root))
            global_count, global_bytes, global_dirs, local_count, local_bytes, local_dirs = map(
                int, stats.split("\t")
            )
            self.assertEqual((global_count, global_bytes, global_dirs), (3, expected_bytes, 1))
            self.assertEqual((local_count, local_bytes, local_dirs), (1, expected_bytes, 1))

            # Toggling the same directory off clears its recursive contribution.
            untoggled = self.run_indexer(
                db,
                "--selection-toggle-directory-ui",
                str(folder),
                "--selection-root",
                str(root),
                data=descendants,
            )
            values = tuple(map(int, untoggled.split("\t")))
            self.assertEqual(values[0], 0)
            self.assertEqual(values[4], 0)
            self.assertEqual(values[5], 0)


if __name__ == "__main__":
    unittest.main()
