#!/usr/bin/env python3
"""Regression checks for the user-local rev.56 beta installer."""
import re
import stat
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "install-eazy-pronto.sh"


class BetaInstallerTests(unittest.TestCase):
    def test_runtime_helpers_are_in_the_download_list(self):
        source = INSTALLER.read_text(encoding="utf-8")
        match = re.search(r"(?ms)^files=\(\n(.*?)^\)", source)
        self.assertIsNotNone(match)
        files = set(re.findall(r"^[ \t]*([A-Za-z0-9_.-]+)[ \t]*$", match.group(1), re.M))
        self.assertTrue(
            {
                "eazy",
                "eazy-index.py",
                "eazy-convert-m3u.py",
                "eazy-live-watch.py",
                "full.c",
                "migrate_eazy_lists.py",
            }.issubset(files)
        )

    def test_main_script_is_executable_before_version_validation(self):
        source = INSTALLER.read_text(encoding="utf-8")
        chmod = source.index('chmod 755 "$TMP/eazy"')
        validate = source.index('installed_version="$("$TMP/eazy" --version 2>&1)"')
        install = source.index('install -m "$mode" "$TMP/$file" "$BIN/$file"')
        self.assertLess(chmod, validate)
        self.assertLess(validate, install)
        self.assertIn('[[ "$file" == "full.c" ]] && mode=644', source)

    def test_notes_editor_remains_executable_in_source_tree(self):
        mode = (ROOT / "eazy-notes-editor").stat().st_mode
        self.assertTrue(mode & stat.S_IXUSR, "eazy-notes-editor must be executable")


if __name__ == "__main__":
    unittest.main()
