#!/usr/bin/env python3
"""Regression tests for selecting the filesystem of the current Eazy directory."""
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EAZY = ROOT / "eazy"
SOURCE = EAZY.read_text(encoding="utf-8")


def bash_function(name: str) -> str:
    match = re.search(
        rf"(?ms)^{re.escape(name)}\(\)\s*\{{\n.*?^\}}",
        SOURCE,
    )
    if not match:
        raise AssertionError(f"Bash function not found: {name}")
    return match.group(0)


class CurrentFilesystemTests(unittest.TestCase):
    def test_info_disco_passes_requested_directory_to_df(self):
        function = bash_function("info_disco")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fake_bin = root / "bin"
            fake_bin.mkdir()
            argument_log = root / "df-arguments.txt"
            fake_df = fake_bin / "df"
            fake_df.write_text(
                "#!/bin/sh\nprintf '%s\\n' \"$*\" > \"$DF_ARGUMENT_LOG\"\n"
                "printf 'Avail Size\\n1073741824 238000000000\\n'\n",
                encoding="utf-8",
            )
            fake_df.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = f"{fake_bin}:/usr/bin:/bin"
            env["DF_ARGUMENT_LOG"] = str(argument_log)
            current = "/mnt/c/Users/Elzita/scripts"
            result = subprocess.run(
                ["bash", "-c", function + '\ninfo_disco "$1"', "bash", current],
                env=env,
                capture_output=True,
                text=True,
                check=True,
            )

            self.assertEqual(result.stdout.strip(), "1073741824 238000000000")
            self.assertEqual(
                argument_log.read_text(encoding="utf-8").strip(),
                f"-B1 --output=avail,size {current}",
            )

    def test_status_header_uses_and_exports_current_directory_path(self):
        status_header = bash_function("eazy_status_header")
        self.assertIn(
            'local atual_dir="${EAZY_HEADER_DISK_PATH:-$(pwd -P 2>/dev/null || pwd)}"',
            status_header,
        )
        self.assertIn('info_disco "$atual_dir"', status_header)
        self.assertIn(
            'EAZY_HEADER_DISK_PATH="${PASTA_ATUAL:-$(pwd -P 2>/dev/null || pwd)}"',
            SOURCE,
        )
        self.assertIn("export EAZY_HEADER_DISK_PATH", SOURCE)


if __name__ == "__main__":
    unittest.main()
