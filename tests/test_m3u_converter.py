#!/usr/bin/env python3
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "eazy-convert-m3u.py"
spec = importlib.util.spec_from_file_location("eazy_convert_m3u", SCRIPT)
converter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(converter)


class M3UConversionTests(unittest.TestCase):
    def test_linux_paths_convert_to_windows_and_preserve_tags(self):
        source = "#EXTM3U\n#EXTINF:-1,Title\n/mnt/c/Media/movie.mp4\n"
        converted = converter.convert_playlist(source, "linux-to-windows", "Ubuntu")
        self.assertEqual(
            converted,
            "#EXTM3U\n#EXTINF:-1,Title\nC:\\Media\\movie.mp4\n",
        )

    def test_windows_paths_convert_to_linux_for_matching_wsl_distro(self):
        self.assertEqual(
            converter.to_linux(r"\\wsl.localhost\Ubuntu\home\user\movie.mp4", "Ubuntu"),
            "/home/user/movie.mp4",
        )
        self.assertEqual(
            converter.to_linux(r"\\wsl.localhost\OtherDistro\home\user\movie.mp4", "Ubuntu"),
            r"\\wsl.localhost\OtherDistro\home\user\movie.mp4",
        )
        self.assertEqual(converter.to_linux(r"D:\Media\movie.mp4", "Ubuntu"), "/mnt/d/Media/movie.mp4")

    def test_auto_writes_new_sibling_without_overwriting_previous_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "list.m3u8"
            original = "#EXTM3U\n/mnt/c/Media/movie.mp4\n"
            source.write_text(original, encoding="utf-8")
            for expected_name in ("list-linux-win.m3u8", "list-linux-win-2.m3u8"):
                run = subprocess.run(
                    [sys.executable, str(SCRIPT), "auto", str(source)],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                result = Path(tmp) / expected_name
                self.assertTrue(result.is_file(), run.stdout + run.stderr)
                self.assertIn("C:\\Media\\movie.mp4", result.read_text(encoding="utf-8-sig"))
                self.assertEqual(source.read_text(encoding="utf-8"), original)

    def test_mixed_slashes_require_explicit_direction(self):
        with self.assertRaises(ValueError):
            converter.detect_direction("/mnt/c/a.mp4\nC:\\b.mp4\n")

    def test_urls_do_not_confuse_windows_path_detection(self):
        text = "#EXTM3U\nhttps://example.test/video\nC:\\Media\\movie.mp4\n"
        self.assertEqual(converter.detect_direction(text), "windows-to-linux")

    def test_detect_only_prints_direction_without_creating_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "windows.m3u"
            source.write_text("C:\\Media\\movie.mp4\n", encoding="utf-8")
            run = subprocess.run(
                [sys.executable, str(SCRIPT), "auto", str(source), "--detect-only"],
                check=True, capture_output=True, text=True,
            )
            self.assertEqual(run.stdout.strip(), "windows-to-linux")
            self.assertEqual(list(Path(tmp).iterdir()), [source])

    def test_converted_playlists_use_direction_specific_output_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            windows_dir = root / "WindowsData"
            linux_dir = root / "LinuxData"
            windows_dir.mkdir()
            linux_dir.mkdir()
            linux_input = root / "linux.m3u"
            linux_input.write_text("/mnt/c/Media/movie.mp4\n", encoding="utf-8")
            subprocess.run(
                [sys.executable, str(SCRIPT), "auto", str(linux_input),
                 "--windows-output-dir", str(windows_dir), "--linux-output-dir", str(linux_dir)],
                check=True, capture_output=True, text=True,
            )
            self.assertTrue((windows_dir / "linux-linux-win.m3u").is_file())

            windows_input = root / "windows.m3u"
            windows_input.write_text("C:\\Media\\movie.mp4\n", encoding="utf-8")
            subprocess.run(
                [sys.executable, str(SCRIPT), "auto", str(windows_input),
                 "--windows-output-dir", str(windows_dir), "--linux-output-dir", str(linux_dir)],
                check=True, capture_output=True, text=True,
            )
            self.assertTrue((linux_dir / "windows-win-linux.m3u").is_file())

    def test_eazy_f9_exposes_integration_and_routes_the_configured_destinations(self):
        eazy = (ROOT / "eazy").read_text(encoding="utf-8")
        self.assertIn('"integration" "Integração Linux/Windows', eazy)
        self.assertIn("eazy_configurar_integracao", eazy)
        self.assertIn('--windows-output-dir "$M3U_WINDOWS_OUT_DIR"', eazy)
        self.assertIn('--linux-output-dir "$M3U_LINUX_OUT_DIR"', eazy)
        self.assertIn("findmnt --noheadings --raw --types", eazy)


if __name__ == "__main__":
    unittest.main()
