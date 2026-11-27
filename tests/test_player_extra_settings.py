#!/usr/bin/env python3
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "eazy").read_text(encoding="utf-8")


def extract_shell_function(name: str) -> str:
    match = re.search(rf"(?m)^{re.escape(name)}\(\) \{{\n", SOURCE)
    if not match:
        raise AssertionError(f"Função não encontrada: {name}")
    end = re.search(r"(?m)^\}\n", SOURCE[match.end():])
    if not end:
        raise AssertionError(f"Fim da função não encontrado: {name}")
    return SOURCE[match.start():match.end() + end.end()]


class PlayerExtraSettingsTests(unittest.TestCase):
    INITIAL = {
        "mpv": "--keep-open=yes --zoom",
        "mplayer": '-vo "x11" --border',
        "cvlc": "",
        "ffplay": "",
    }

    def run_editor(self, new_value: str = "", player: str = "mplayer", action: str = "edit"):
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            menu_log = temp / "menu.log"
            menu_count = temp / "menu.count"
            input_log = temp / "input.log"
            config_dir = temp / "config"
            config_file = config_dir / "config"
            config_dir.mkdir()
            player_var = {
                "mpv": "PLAYER_EXTRA_MPV",
                "mplayer": "PLAYER_EXTRA_MPLAYER",
                "cvlc": "PLAYER_EXTRA_CVLC",
                "ffplay": "PLAYER_EXTRA_FFPLAY",
            }[player]
            config_file.write_text(
                f'UNRELATED="preserve me"\n{player_var}={self.INITIAL[player]!r}\n',
                encoding="utf-8",
            )
            shell = "\n".join(
                [
                    "whiptail() {",
                    "  local is_menu=0 is_input=0 title='' args=\"$*\" menu_count",
                    "  while (($#)); do",
                    "    case \"$1\" in",
                    "      --menu) is_menu=1 ;;",
                    "      --inputbox) is_input=1 ;;",
                    "      --title) shift; title=${1-} ;;",
                    "    esac",
                    "    shift",
                    "  done",
                    "  if [[ $is_menu == 1 && $title == 'F9 — Parâmetros extras dos players' ]]; then",
                    "    menu_count=$(cat \"$TEST_MENU_COUNT\" 2>/dev/null || printf 0)",
                    "    menu_count=$((menu_count + 1))",
                    "    printf '%s' \"$menu_count\" > \"$TEST_MENU_COUNT\"",
                    "    printf '%s\\n' \"$args\" >> \"$TEST_MENU_LOG\"",
                    "    if [[ $menu_count == 1 ]]; then printf '%s' \"$TEST_PLAYER\" >&3; else return 1; fi",
                    "  elif [[ $is_menu == 1 ]]; then",
                    "    printf '%s\\n' \"$args\" >> \"$TEST_MENU_LOG\"",
                    "    printf '%s' \"$TEST_ACTION\" >&3",
                    "  elif [[ $is_input == 1 ]]; then",
                    "    printf '%s\\n' \"$args\" >> \"$TEST_INPUT_LOG\"",
                    "    printf '%s' \"$TEST_NEW_VALUE\" >&3",
                    "  fi",
                    "  return 0",
                    "}",
                    'CONFIG_DIR="$TEST_CONFIG_DIR"',
                    'CONFIG_FILE="$TEST_CONFIG_FILE"',
                    extract_shell_function("eazy_config_set_value"),
                    extract_shell_function("eazy_config_unset_value"),
                    "PLAYER_EXTRA_MPV='--keep-open=yes --zoom'",
                    "PLAYER_EXTRA_MPLAYER='-vo \"x11\" --border'",
                    "PLAYER_EXTRA_CVLC=''",
                    "PLAYER_EXTRA_FFPLAY=''",
                    extract_shell_function("eazy_player_extra_preview"),
                    extract_shell_function("eazy_configurar_parametros_players"),
                    "eazy_configurar_parametros_players",
                    'source "$CONFIG_FILE"',
                    f"printf 'FINAL=%s\\n' \"${{{player_var}}}\"",
                    "printf 'UNRELATED=%s\\n' \"$UNRELATED\"",
                ]
            )
            env = os.environ.copy()
            env.update(
                TEST_MENU_LOG=str(menu_log),
                TEST_MENU_COUNT=str(menu_count),
                TEST_INPUT_LOG=str(input_log),
                TEST_CONFIG_DIR=str(config_dir),
                TEST_CONFIG_FILE=str(config_file),
                TEST_NEW_VALUE=new_value,
                TEST_PLAYER=player,
                TEST_ACTION=action,
            )
            result = subprocess.run(
                ["bash", "-c", shell], capture_output=True, text=True, env=env, check=True
            )
            return (
                result.stdout,
                menu_log.read_text(encoding="utf-8"),
                input_log.read_text(encoding="utf-8") if input_log.exists() else "",
                config_file.read_text(encoding="utf-8"),
            )

    def test_f9_and_configuration_assistant_use_the_player_editor(self):
        self.assertIn('"player_extra" "Players e parâmetros extras', SOURCE)
        self.assertIn("player_extra) eazy_configurar_parametros_players", SOURCE)
        self.assertIn("eazy_configurar_parametros_players\n\n    # Checkbox", SOURCE)

    def test_selected_player_can_edit_and_save_a_replacement(self):
        stdout, menus, input_box, config = self.run_editor('--vo "gl" --zoom')
        self.assertIn('MPlayer | -vo "x11" --border', menus)
        self.assertIn("Editar o valor atual (campo preenchido)", menus)
        self.assertIn('-vo "x11" --border', input_box)
        self.assertIn('FINAL=--vo "gl" --zoom', stdout)
        self.assertIn("UNRELATED=preserve me", stdout)
        self.assertIn("PLAYER_EXTRA_MPLAYER=", config)

    def test_clearing_mpv_in_editor_removes_persisted_config_entry(self):
        stdout, menus, input_box, config = self.run_editor("", player="mpv")
        self.assertIn("mpv     | --keep-open=yes --zoom", menus)
        self.assertIn("Substituir por uma nova linha", input_box)
        self.assertIn("--keep-open=yes --zoom", input_box)
        self.assertIn("FINAL=\n", stdout)
        self.assertIn("UNRELATED=preserve me", stdout)
        self.assertNotRegex(config, r"(?m)^PLAYER_EXTRA_MPV=")

    def test_clear_action_removes_mpv_and_mplayer_values(self):
        for player, variable in (("mpv", "PLAYER_EXTRA_MPV"), ("mplayer", "PLAYER_EXTRA_MPLAYER")):
            with self.subTest(player=player):
                stdout, menus, input_box, config = self.run_editor(player=player, action="clear")
                self.assertIn("Remover todos os parâmetros deste player", menus)
                self.assertEqual(input_box, "")
                self.assertIn("FINAL=\n", stdout)
                self.assertNotRegex(config, rf"(?m)^{variable}=")
                self.assertIn('UNRELATED="preserve me"', config)

    def test_clearing_mplayer_in_editor_removes_its_saved_value(self):
        stdout, _menus, input_box, config = self.run_editor("")
        self.assertIn('-vo "x11" --border', input_box)
        self.assertIn("FINAL=\n", stdout)
        self.assertNotRegex(config, r"(?m)^PLAYER_EXTRA_MPLAYER=")

    def test_replace_action_starts_with_an_empty_field(self):
        stdout, menus, input_box, config = self.run_editor("-fs -zoom", action="replace")
        self.assertIn("Substituir por uma nova linha (campo vazio)", menus)
        self.assertNotIn('-vo "x11" --border', input_box)
        self.assertIn("FINAL=-fs -zoom", stdout)
        self.assertIn("PLAYER_EXTRA_MPLAYER=", config)


if __name__ == "__main__":
    unittest.main()
