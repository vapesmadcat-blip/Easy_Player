#!/usr/bin/env python3
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "eazy-win.py"
spec = importlib.util.spec_from_file_location("eazy_win", SCRIPT)
eazy_win = importlib.util.module_from_spec(spec)
spec.loader.exec_module(eazy_win)


class WindowsEditionTests(unittest.TestCase):
    def test_settings_round_trip(self):
        with tempfile.TemporaryDirectory() as temp:
            config = Path(temp) / "AppData" / "integration.json"
            settings = eazy_win.default_integration_settings()
            settings["linux_output_dir"] = r"\\wsl.localhost\Ubuntu\home\demo\EazyData"
            eazy_win.save_integration_settings(settings, config)
            self.assertEqual(eazy_win.load_integration_settings(config), settings)

    def test_f9_updates_and_persists_windows_destination(self):
        settings = eazy_win.default_integration_settings()
        with patch.object(eazy_win, "read_key", side_effect=["1", "0"]), \
             patch("builtins.input", return_value=r"C:\Users\demo\EazyData"), \
             patch.object(eazy_win, "save_integration_settings") as save:
            eazy_win.configure_integration(settings)
        self.assertEqual(settings["windows_output_dir"], r"C:\Users\demo\EazyData")
        save.assert_called_once_with(settings)

    def test_enter_on_m3u_offers_convert_action(self):
        playlist = Path("sample.m3u8")
        settings = eazy_win.default_integration_settings()
        with patch.object(eazy_win, "read_key", return_value="2"), \
             patch.object(eazy_win, "convert_m3u", return_value="converted") as convert:
            self.assertEqual(eazy_win.handle_m3u_enter(playlist, settings), "converted")
        convert.assert_called_once_with(playlist, settings)

    def test_browser_enter_routes_m3u_to_its_menu(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            playlist = root / "sample.m3u"
            playlist.write_text("#EXTM3U\n", encoding="utf-8")
            settings = eazy_win.default_integration_settings()
            with patch.object(eazy_win, "read_key", side_effect=["enter", "q"]), \
                 patch.object(eazy_win, "draw"), \
                 patch.object(eazy_win, "handle_m3u_enter", return_value="menu opened") as menu:
                self.assertEqual(eazy_win.run(root, settings), 0)
            menu.assert_called_once_with(playlist, settings)

    def test_m3u_conversion_routes_linux_paths_to_windows_destination_and_preserves_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            windows_dir = root / "WindowsData"
            linux_dir = root / "LinuxData"
            windows_dir.mkdir()
            linux_dir.mkdir()
            source = root / "linux.m3u"
            original = "#EXTM3U\n/mnt/c/Media/movie.mp4\n"
            source.write_text(original, encoding="utf-8")
            settings = {
                "windows_output_dir": str(windows_dir),
                "linux_output_dir": str(linux_dir),
                "wsl_distro": "Ubuntu",
            }
            message = eazy_win.convert_m3u(source, settings)
            converted = windows_dir / "linux-linux-win.m3u"
            self.assertTrue(converted.is_file(), message)
            self.assertIn("C:\\Media\\movie.mp4", converted.read_text(encoding="utf-8-sig"))
            self.assertEqual(source.read_text(encoding="utf-8"), original)

    def test_m3u_conversion_routes_windows_paths_to_linux_destination(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            windows_dir = root / "WindowsData"
            linux_dir = root / "LinuxData"
            windows_dir.mkdir()
            linux_dir.mkdir()
            source = root / "windows.m3u"
            original = "#EXTM3U\nC:\\Media\\movie.mp4\n"
            source.write_text(original, encoding="utf-8")
            settings = {
                "windows_output_dir": str(windows_dir),
                "linux_output_dir": str(linux_dir),
                "wsl_distro": "Ubuntu",
            }
            message = eazy_win.convert_m3u(source, settings)
            converted = linux_dir / "windows-win-linux.m3u"
            self.assertTrue(converted.is_file(), message)
            self.assertIn("/mnt/c/Media/movie.mp4", converted.read_text(encoding="utf-8-sig"))
            self.assertEqual(source.read_text(encoding="utf-8"), original)

    def test_m3u_extensions_are_case_insensitive_and_volume_query_is_platform_aware(self):
        self.assertIn(Path("example.M3U8").suffix.lower(), (".m3u", ".m3u8"))
        if eazy_win.os.name != "nt":
            self.assertIn("só está disponível", eazy_win.windows_volume_summary())


if __name__ == "__main__":
    unittest.main()
