#!/usr/bin/env python3
"""Initial, dependency-free Windows edition/preview for Easy.

It demonstrates local navigation and yellow selection, and provides M3U
conversion through the shared helper plus persisted Windows/WSL destinations.
It does not yet share the Linux edition's SQLite database or full file actions.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

VERSION = "5.2.0"
REVISION = 51
COLOR = False
CONFIG_FILE = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")) / "Easy" / "integration.json"
M3U_HELPER = Path(__file__).resolve().with_name("eazy-convert-m3u.py")


def detect_wsl_distro() -> str:
    if os.name == "nt":
        try:
            result = subprocess.run(
                ["wsl.exe", "--list", "--quiet"], capture_output=True,
                text=True, timeout=5, check=False,
            )
            names = [line.replace("\x00", "").strip() for line in result.stdout.splitlines()]
            names = [name for name in names if name]
            if names:
                return names[0]
        except (OSError, subprocess.SubprocessError):
            pass
    return "Ubuntu"


def default_integration_settings() -> dict[str, str]:
    return {
        "windows_output_dir": str(Path.home() / "EazyData"),
        "linux_output_dir": "",
        "wsl_distro": detect_wsl_distro(),
    }


def load_integration_settings(config_path: Path = CONFIG_FILE) -> dict[str, str]:
    settings = default_integration_settings()
    try:
        saved = json.loads(config_path.read_text(encoding="utf-8"))
        if isinstance(saved, dict):
            for key in settings:
                if isinstance(saved.get(key), str):
                    settings[key] = saved[key]
    except (OSError, UnicodeError, json.JSONDecodeError):
        pass
    return settings


def save_integration_settings(settings: dict[str, str], config_path: Path = CONFIG_FILE) -> None:
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(settings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def enable_terminal_colors() -> None:
    """Enable VT processing in a Windows console when the host supports it."""
    global COLOR
    if os.name == "nt":
        try:
            import ctypes

            kernel = ctypes.windll.kernel32
            handle = kernel.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
            mode = ctypes.c_uint()
            if kernel.GetConsoleMode(handle, ctypes.byref(mode)):
                COLOR = bool(kernel.SetConsoleMode(handle, mode.value | 0x0004))
        except (AttributeError, OSError):
            COLOR = False
    else:
        COLOR = sys.stdout.isatty() and os.environ.get("TERM") != "dumb"


def clear_screen() -> None:
    if os.name == "nt" and not COLOR:
        os.system("cls")
    else:
        print("\x1b[2J\x1b[H", end="", flush=True)


def yellow(text: str) -> str:
    return f"\x1b[33;1m{text}\x1b[0m" if COLOR else text


def read_key() -> str:
    """Read one key without requiring curses, fzf, or a POSIX shell."""
    if os.name == "nt":
        import msvcrt

        char = msvcrt.getwch()
        if char in ("\x00", "\xe0"):
            return {
                "H": "up",
                "P": "down",
                "K": "left",
                "M": "right",
                "C": "f9",
            }.get(msvcrt.getwch(), "unknown")
        if char == "\x0b":
            return "ctrl-k"
        if char == "\x1b":
            return "escape"
        if char in ("\r", "\n"):
            return "enter"
        if char in ("\x08", "\x7f"):
            return "backspace"
        if char == " ":
            return "space"
        return char.lower()

    import termios
    import tty

    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        char = sys.stdin.read(1)
        if char == "\x1b":
            sequence = sys.stdin.read(1)
            if sequence in ("[", "O"):
                while True:
                    final = sys.stdin.read(1)
                    sequence += final
                    if final in "@ABCDEFGHIJKLMNOPQRSTUVWXYZ\\^_`abcdefghijklmnopqrstuvwxyz{|}~":
                        break
            return {
                "[A": "up",
                "[B": "down",
                "[D": "left",
                "[C": "right",
                "[20~": "f9",
            }.get(sequence, "escape")
        if char == "\x0b":
            return "ctrl-k"
        if char in ("\r", "\n"):
            return "enter"
        if char in ("\x08", "\x7f"):
            return "backspace"
        if char == " ":
            return "space"
        if char == "\x03":
            return "q"
        return char.lower()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def scan_directory(directory: Path) -> list[tuple[Path, bool, int]]:
    """List one directory level using the host OS APIs; never shells out."""
    entries: list[tuple[Path, bool, int]] = []
    with os.scandir(directory) as iterator:
        for entry in iterator:
            path = Path(entry.path)
            try:
                is_directory = entry.is_dir(follow_symlinks=True)
                size = 0 if is_directory else entry.stat(follow_symlinks=False).st_size
            except OSError:
                is_directory, size = False, 0
            entries.append((path, is_directory, size))
    entries.sort(key=lambda row: (not row[1], row[0].name.casefold(), row[0].name))
    return entries


def human_size(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.0f} {unit}" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} B"


def key_for_directory(directory: Path) -> str:
    # Keep the original spelling. Do not lowercase paths: Windows can expose
    # directories configured for case-sensitive names.
    return os.path.abspath(os.fspath(directory))


def action_targets(directory: Path, entries: list[tuple[Path, bool, int]], cursor: int,
                   selection_by_directory: dict[str, set[str]]) -> list[Path]:
    """Use local yellow entries first; otherwise only a file under the cursor."""
    local = selection_by_directory.setdefault(key_for_directory(directory), set())
    visible = {os.fspath(path): (path, is_directory) for path, is_directory, _ in entries}
    selected = [visible[item][0] for item in sorted(local) if item in visible]
    if selected:
        return selected
    if 0 <= cursor < len(entries):
        path, is_directory, _ = entries[cursor]
        if not is_directory:
            return [path]
    return []


def draw(directory: Path, entries: list[tuple[Path, bool, int]], cursor: int,
         selected: set[str], message: str = "") -> None:
    clear_screen()
    width, height = shutil.get_terminal_size((100, 30))
    print(f"Eazy Windows — preview {VERSION} rev.{REVISION}")
    print(f"Pasta: {directory}")
    print("↑/↓ mover  Enter abrir/M3U  Backspace voltar  Espaço amarelo  Ctrl+K ações  F9 integração  Q sair")
    print("─" * max(20, min(width, 110)))

    visible_rows = max(4, height - 8)
    if entries:
        first = max(0, min(cursor - visible_rows // 2, len(entries) - visible_rows))
        last = min(len(entries), first + visible_rows)
        for index in range(first, last):
            path, is_directory, size = entries[index]
            marker = "● " if os.fspath(path) in selected else "  "
            kind = "[DIR] " if is_directory else "      "
            detail = "" if is_directory else human_size(size)
            row = f"{marker}{kind}{path.name}"
            if detail:
                row = f"{row:<{max(20, width - 15)}} {detail:>8}"
            if index == cursor:
                row = f"> {row}"
            if os.fspath(path) in selected:
                row = yellow(row)
            print(row[:max(20, width)])
        if first:
            print(f"… {first} item(ns) acima")
        if last < len(entries):
            print(f"… {len(entries) - last} item(ns) abaixo")
    else:
        print("(pasta vazia)")
    if message:
        print(f"\n{message}")


def show_actions(directory: Path, entries: list[tuple[Path, bool, int]], cursor: int,
                 selection_by_directory: dict[str, set[str]]) -> None:
    targets = action_targets(directory, entries, cursor, selection_by_directory)

    clear_screen()
    print("Ctrl+K — demonstração de ações")
    print(f"Pasta: {directory}")
    if targets:
        print(f"Alvos (amarelos locais; se não houver, arquivo sob o cursor): {len(targets)}")
        for path in targets[:10]:
            print(f"  {path}")
        if len(targets) > 10:
            print(f"  … e mais {len(targets) - 10}")
    else:
        print("Nenhum arquivo-alvo. As opções sem arquivo continuam disponíveis.")
    print("\n1  Mostrar resumo dos alvos")
    print("M  Manutenção de exemplo (não precisa de arquivo)")
    print("0  Voltar")
    choice = read_key()
    if choice == "1":
        total = sum(path.stat().st_size for path in targets if path.is_file())
        clear_screen()
        print(f"{len(targets)} alvo(s); {human_size(total)} no total.")
        for path in targets[:20]:
            print(path)
        input("\nEnter para voltar…")
    elif choice == "m":
        clear_screen()
        print("Ação sem alvo executada como demonstração: manutenção pode abrir sem seleção.")
        input("\nEnter para voltar…")


def open_file(path: Path) -> str:
    try:
        if os.name == "nt":
            os.startfile(os.fspath(path))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", os.fspath(path)])
        else:
            subprocess.Popen(["xdg-open", os.fspath(path)])
        return f"Aberto pelo aplicativo padrão: {path.name}"
    except (OSError, subprocess.SubprocessError) as exc:
        return f"Não foi possível abrir {path.name}: {exc}"


def windows_volume_summary() -> str:
    if os.name != "nt":
        return "A consulta de volumes do Windows só está disponível ao executar a edição Windows."
    command = (
        "Get-Volume | Where-Object DriveLetter | "
        "Select-Object DriveLetter,FileSystem,DriveType | Format-Table -AutoSize | Out-String"
    )
    try:
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", command],
            capture_output=True, text=True, timeout=10, check=False,
        )
        return result.stdout.strip() or result.stderr.strip() or "Nenhum volume montado foi listado."
    except (OSError, subprocess.SubprocessError) as exc:
        return f"Não foi possível consultar os volumes: {exc}"


def configure_integration(settings: dict[str, str]) -> None:
    while True:
        clear_screen()
        print("F9 — Integração Windows / WSL")
        print(f"Destino Windows: {settings.get('windows_output_dir', '') or '(não definido)'}")
        print(f"Destino Linux/WSL: {settings.get('linux_output_dir', '') or '(não definido)'}")
        print(f"Distribuição WSL: {settings.get('wsl_distro', 'Ubuntu')}")
        print("\n1  Configurar pasta Windows (saída Linux → Windows)")
        print("2  Configurar pasta Linux/WSL (saída Windows → Linux)")
        print("3  Consultar volumes montados e sistemas de arquivos")
        print("4  Configurar nome da distribuição WSL")
        print("0  Voltar")
        choice = read_key()
        if choice in ("0", "escape", "q"):
            return
        if choice == "3":
            clear_screen()
            print(windows_volume_summary())
            input("\nEnter para voltar…")
            continue
        if choice == "4":
            value = input(f"Nome da distribuição WSL [{settings.get('wsl_distro', 'Ubuntu')}]: ").strip()
            if value:
                settings["wsl_distro"] = value
                save_integration_settings(settings)
            continue
        if choice not in ("1", "2"):
            continue
        key = "windows_output_dir" if choice == "1" else "linux_output_dir"
        current = settings.get(key, "")
        label = "Windows" if choice == "1" else "Linux/WSL (UNC, ex.: \\\\wsl.localhost\\Ubuntu\\home\\user\\EazyData)"
        value = input(f"Pasta de saída {label} [{current}]: ").strip()
        if value:
            settings[key] = value
            save_integration_settings(settings)


def convert_m3u(path: Path, settings: dict[str, str]) -> str:
    if not M3U_HELPER.is_file():
        return f"Conversor ausente ao lado do aplicativo: {M3U_HELPER.name}"
    detect = subprocess.run(
        [sys.executable, str(M3U_HELPER), "auto", str(path), "--detect-only"],
        capture_output=True, text=True, check=False,
    )
    if detect.returncode != 0:
        return detect.stderr.strip() or detect.stdout.strip() or "Não foi possível detectar a direção."
    direction = detect.stdout.strip()
    dest_key = "windows_output_dir" if direction == "linux-to-windows" else "linux_output_dir"
    destination = settings.get(dest_key, "").strip()
    if not destination:
        return "Configure a pasta de destino no menu F9 → Integração e tente novamente."
    dest_path = Path(destination)
    if not dest_path.is_dir():
        clear_screen()
        answer = input(f"A pasta de destino não existe:\n{destination}\nCriar agora? [s/N] ").strip().lower()
        if answer not in ("s", "sim", "y", "yes"):
            return "Conversão cancelada; o destino não foi criado."
        try:
            dest_path.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            return f"Não foi possível criar a pasta de destino: {exc}"
    run = subprocess.run(
        [sys.executable, str(M3U_HELPER), "auto", str(path),
         "--windows-output-dir", settings.get("windows_output_dir", ""),
         "--linux-output-dir", settings.get("linux_output_dir", ""),
         "--distro", settings.get("wsl_distro", "Ubuntu")],
        capture_output=True, text=True, check=False,
    )
    if run.returncode == 0:
        return f"{run.stdout.strip()}\n\nO original foi preservado."
    return run.stderr.strip() or run.stdout.strip() or "Falha na conversão."


def handle_m3u_enter(path: Path, settings: dict[str, str]) -> str:
    clear_screen()
    print(f"Playlist: {path}")
    print("\nO que deseja fazer?")
    print("1  Abrir/reproduzir com o aplicativo padrão do Windows")
    print("2  Converter caminhos automaticamente")
    print("0  Cancelar")
    choice = read_key()
    if choice == "1":
        return open_file(path)
    if choice == "2":
        return convert_m3u(path, settings)
    return ""


def self_test() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        (root / "folder").mkdir()
        (root / "small.txt").write_text("Easy", encoding="utf-8")
        rows = scan_directory(root)
        assert len(rows) == 2
        assert rows[0][1] is True
        assert rows[1][0].name == "small.txt" and rows[1][2] == 4
        local = {key_for_directory(root): {os.fspath(root / "folder")}}
        assert action_targets(root, rows, 1, local) == [root / "folder"]
        assert action_targets(root, rows, 1, {}) == [root / "small.txt"]
        assert action_targets(root, rows, 0, {}) == []
        cfg = root / "settings" / "integration.json"
        settings = default_integration_settings()
        settings["linux_output_dir"] = r"\\wsl.localhost\Ubuntu\home\demo\EazyData"
        save_integration_settings(settings, cfg)
        assert load_integration_settings(cfg)["linux_output_dir"] == settings["linux_output_dir"]
    assert Path("example.M3U8").suffix.lower() in (".m3u", ".m3u8")
    print("Windows edition self-test: OK (navigation, selection, settings).")


def run(start: Path, settings: dict[str, str] | None = None) -> int:
    settings = settings if settings is not None else load_integration_settings()
    current = Path(os.path.abspath(os.fspath(start.expanduser())))
    if not current.is_dir():
        print(f"Não é uma pasta acessível: {current}", file=sys.stderr)
        return 2

    selection_by_directory: dict[str, set[str]] = {}
    cursor_by_directory: dict[str, int] = {}
    message = ""
    while True:
        try:
            entries = scan_directory(current)
            error = ""
        except OSError as exc:
            entries, error = [], f"Falha ao listar a pasta: {exc}"
        cursor = min(cursor_by_directory.get(key_for_directory(current), 0), max(0, len(entries) - 1))
        local_selection = selection_by_directory.setdefault(key_for_directory(current), set())
        draw(current, entries, cursor, local_selection, error or message)
        message = ""
        key = read_key()

        if key == "q":
            return 0
        if key == "up" and entries:
            cursor = max(0, cursor - 1)
        elif key == "down" and entries:
            cursor = min(len(entries) - 1, cursor + 1)
        elif key in ("backspace", "left"):
            parent = current.parent
            if parent != current:
                current = parent
                continue
        elif key == "space" and entries:
            item = os.fspath(entries[cursor][0])
            if item in local_selection:
                local_selection.remove(item)
            else:
                local_selection.add(item)
        elif key == "ctrl-k":
            show_actions(current, entries, cursor, selection_by_directory)
        elif key == "f9":
            configure_integration(settings)
        elif key == "enter" and entries:
            path, is_directory, _ = entries[cursor]
            if is_directory:
                cursor_by_directory[key_for_directory(current)] = cursor
                current = path
                continue
            elif path.suffix.lower() in (".m3u", ".m3u8"):
                message = handle_m3u_enter(path, settings)
            else:
                message = open_file(path)
        cursor_by_directory[key_for_directory(current)] = cursor


def main() -> int:
    parser = argparse.ArgumentParser(description=f"Edição Windows preview do Eazy {VERSION} rev.{REVISION}")
    parser.add_argument("path", nargs="?", default=".", help="pasta inicial; aceita caminho local ou UNC no Windows")
    parser.add_argument("--self-test", action="store_true", help="testa listagem e metadados sem abrir a TUI")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    enable_terminal_colors()
    try:
        return run(Path(args.path))
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
