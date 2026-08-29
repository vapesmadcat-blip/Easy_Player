"""eazy Windows — navegador e organizador multimídia em Python.

Versão Windows do eazy 3.0, sem dependências obrigatórias de Linux.
Uso: python eazy_windows.py [caminho]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterable

VERSION = "3.0.56-win1"
APP_DIR = Path(os.environ.get("APPDATA", Path.home())) / "eazy"
CONFIG_FILE = APP_DIR / "config.json"
HISTORY_FILE = APP_DIR / "history.json"
QUEUES_DIR = APP_DIR / "queues"
SEARCH_DIR = APP_DIR / "saved_searches"
NOTES_DIR = APP_DIR / "notes"
PLAYLISTS_DIR = Path.home() / "Playlists"

VIDEO = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".wmv", ".m4v"}
AUDIO = {".mp3", ".flac", ".wav", ".ogg", ".m4a", ".aac", ".wma"}
IMAGE = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"}
TEXT = {".txt", ".md", ".csv", ".log", ".json", ".py", ".ini", ".cfg"}
PLAYLIST = {".m3u", ".m3u8", ".pls"}


def ensure_dirs() -> None:
    for path in (APP_DIR, QUEUES_DIR, SEARCH_DIR, NOTES_DIR, PLAYLISTS_DIR):
        path.mkdir(parents=True, exist_ok=True)


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default


def save_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def pause() -> None:
    input("\nPressione Enter para continuar...")


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)


def file_kind(path: Path) -> str:
    if path.is_dir(): return "DIR"
    suffix = path.suffix.lower()
    if suffix in VIDEO: return "VIDEO"
    if suffix in AUDIO: return "AUDIO"
    if suffix in IMAGE: return "IMAGE"
    if suffix in PLAYLIST: return "LIST"
    if suffix in TEXT: return "TEXT"
    if suffix == ".pdf": return "PDF"
    return "FILE"


def format_size(size: int) -> str:
    units = ("B", "KB", "MB", "GB", "TB")
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return str(size)


def recursive_size(path: Path) -> int:
    if path.is_file():
        try: return path.stat().st_size
        except OSError: return 0
    total = 0
    try:
        for item in path.rglob("*"):
            if item.is_file():
                try: total += item.stat().st_size
                except OSError: pass
    except OSError: pass
    return total


def list_entries(path: Path, sort_mode: str = "name") -> list[Path]:
    try: entries = list(path.iterdir())
    except OSError as exc:
        print(f"Não foi possível abrir {path}: {exc}")
        return []
    entries.sort(key=lambda p: p.name.lower())
    if sort_mode == "size": entries.sort(key=recursive_size, reverse=True)
    elif sort_mode == "date": entries.sort(key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)
    return entries


def hash_file(path: Path, chunk: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(chunk), b""):
            digest.update(block)
    return digest.hexdigest()


def duplicate_scan(root: Path) -> list[list[Path]]:
    by_size: dict[int, list[Path]] = {}
    print(f"Inventariando: {root}")
    for path in root.rglob("*"):
        if path.is_file():
            try: by_size.setdefault(path.stat().st_size, []).append(path)
            except OSError: pass
    groups: dict[str, list[Path]] = {}
    candidates = [p for values in by_size.values() if len(values) > 1 for p in values]
    for index, path in enumerate(candidates, 1):
        try: groups.setdefault(f"{path.stat().st_size}:{hash_file(path)}", []).append(path)
        except (OSError, PermissionError): pass
        if index % 20 == 0: print(f"  comparados: {index}/{len(candidates)}")
    return [values for values in groups.values() if len(values) > 1]


def search_files(root: Path, name: str = "", extension: str = "", content: str = "", min_size: int = 0, max_size: int = 0) -> list[Path]:
    results = []
    for path in root.rglob("*"):
        if not path.is_file(): continue
        if name and name.lower() not in path.name.lower(): continue
        if extension and path.suffix.lower() != extension.lower(): continue
        try: size = path.stat().st_size
        except OSError: continue
        if size < min_size or (max_size and size > max_size): continue
        if content:
            try:
                if content.lower() not in path.read_text(encoding="utf-8", errors="ignore").lower(): continue
            except OSError: continue
        results.append(path)
    return results


def play(path: Path) -> None:
    player = shutil.which("mpv") or shutil.which("vlc") or shutil.which("wmplayer")
    if player:
        try: subprocess.Popen([player, str(path)])
        except OSError as exc: print(f"Falha ao abrir o player: {exc}")
    elif os.name == "nt":
        os.startfile(str(path))  # type: ignore[attr-defined]
    else:
        print("Nenhum player encontrado.")


def open_path(path: Path) -> None:
    if os.name == "nt": os.startfile(str(path))  # type: ignore[attr-defined]
    elif shutil.which("xdg-open"): subprocess.Popen(["xdg-open", str(path)])
    else: print(path)


def save_history(path: Path) -> None:
    history = load_json(HISTORY_FILE, [])
    item = str(path)
    history = [item] + [x for x in history if x != item]
    save_json(HISTORY_FILE, history[:200])


def write_playlist(items: list[Path], target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("#EXTM3U\n" + "\n".join(str(x) for x in items) + "\n", encoding="utf-8")


def choose_items(items: list[Path]) -> list[Path]:
    if not items: return []
    print("\nItens disponíveis:")
    for i, item in enumerate(items, 1): print(f" {i:>3}. [{file_kind(item):5}] {item}")
    raw = input("Números separados por vírgula, intervalo (1-3) ou * para todos: ").strip()
    if raw == "*": return items
    selected: list[Path] = []
    for token in raw.split(","):
        token = token.strip()
        try:
            if "-" in token:
                a, b = (int(x) for x in token.split("-", 1))
                selected.extend(items[max(1, a)-1:min(len(items), b)])
            else: selected.append(items[int(token)-1])
        except (ValueError, IndexError): pass
    return list(dict.fromkeys(selected))


def notes_menu() -> None:
    while True:
        clear(); notes = sorted(NOTES_DIR.glob("*.txt"))
        print("=== NOTAS ===\n")
        for i, note in enumerate(notes, 1): print(f"{i}. {note.stem}")
        print("\nN nova | E número editar | D número apagar | Enter voltar")
        cmd = input("> ").strip()
        if not cmd: return
        if cmd.lower() == "n":
            name = input("Nome da nota: ").strip() or f"nota_{int(time.time())}"
            content = input("Texto (uma linha; edite o arquivo depois se desejar): ")
            (NOTES_DIR / f"{name}.txt").write_text(content + "\n", encoding="utf-8")
        elif cmd[:1].lower() in {"e", "d"}:
            try: note = notes[int(cmd[1:].strip()) - 1]
            except (ValueError, IndexError): continue
            if cmd[:1].lower() == "e":
                content = input(f"Novo texto para {note.name}: ")
                note.write_text(content + "\n", encoding="utf-8")
            else: note.unlink(missing_ok=True)


def maintenance(root: Path) -> None:
    clear(); print("=== MANUTENÇÃO ===\n")
    print("1. Validar playlists e referências")
    print("2. Encontrar duplicados")
    print("3. Limpar diretórios vazios")
    print("0. Voltar")
    cmd = input("> ").strip()
    if cmd == "1":
        for playlist in PLAYLISTS_DIR.glob("*.m3u*"):
            lines = playlist.read_text(encoding="utf-8", errors="ignore").splitlines()
            missing = [line for line in lines if line and not line.startswith("#") and not Path(line).exists()]
            print(f"\n{playlist.name}: {len(missing)} referência(s) ausente(s)")
            for item in missing[:20]: print(f"  ✗ AUSENTE {item}")
            if missing and input("Corrigir removendo apenas entradas ausentes? (S/N): ").strip().upper() == "S":
                keep = [line for line in lines if line.startswith("#") or not line or Path(line).exists()]
                playlist.write_text("\n".join(keep) + "\n", encoding="utf-8")
                print("Correção concluída; nenhum arquivo físico foi apagado.")
        pause()
    elif cmd == "2":
        groups = duplicate_scan(root)
        clear(); print(f"=== DUPLICADOS: {len(groups)} grupo(s) ===\n")
        for i, group in enumerate(groups, 1):
            print(f"Grupo {i} — {format_size(recursive_size(group[0]))}")
            for item in group: print(f"  {item}")
        pause()
    elif cmd == "3":
        empty = [p for p in root.rglob("*") if p.is_dir() and not any(p.iterdir())]
        print(f"Diretórios vazios encontrados: {len(empty)}")
        if empty and input("Remover? (S/N): ").strip().upper() == "S":
            for p in sorted(empty, reverse=True):
                try: p.rmdir()
                except OSError: pass
        pause()


def browser(start: Path) -> None:
    state = load_json(CONFIG_FILE, {"sort": "name"})
    current = start.expanduser().resolve() if start.exists() else Path.home()
    while True:
        clear(); entries = list_entries(current, state.get("sort", "name"))
        print(f"eazy {VERSION} | {current} | ordenação: {state.get('sort', 'name')}\n")
        print("[DIR] ..")
        for i, item in enumerate(entries, 1):
            size = format_size(recursive_size(item)) if item.is_dir() else format_size(item.stat().st_size)
            print(f"{i:>3}. [{file_kind(item):5}] {item.name:<42} {size:>10}")
        print("\nEnter número | S buscar | D duplicados | Q filas | P playlist | N notas | M manutenção | O ordenação | X sair")
        cmd = input("> ").strip()
        if cmd.lower() == "x":
            state["last_dir"] = str(current); save_json(CONFIG_FILE, state); return
        if cmd.lower() == "s":
            name = input("Nome contém (vazio = qualquer): ")
            ext = input("Extensão (ex.: .pdf, vazio = qualquer): ")
            content = input("Conteúdo (vazio = não pesquisar): ")
            results = search_files(current, name, ext, content)
            clear(); print(f"=== RESULTADOS: {len(results)} ===\n"); chosen = choose_items(results)
            if chosen and input("Abrir o primeiro? (S/N): ").strip().upper() == "S": open_path(chosen[0])
            pause(); continue
        if cmd.lower() == "d": maintenance(current); continue
        if cmd.lower() == "m": maintenance(current); continue
        if cmd.lower() == "n": notes_menu(); continue
        if cmd.lower() == "o":
            state["sort"] = {"name": "size", "size": "date", "date": "name"}.get(state.get("sort", "name"), "name"); save_json(CONFIG_FILE, state); continue
        if cmd.lower() == "q":
            items = choose_items(entries)
            if items:
                queue = QUEUES_DIR / "queue_1.json"; save_json(queue, [str(x) for x in items]); print("Fila salva em", queue); pause()
            continue
        if cmd.lower() == "p":
            items = choose_items(entries)
            if items:
                target = PLAYLISTS_DIR / (input("Nome da playlist (sem extensão): ").strip() or "playlist")
                write_playlist(items, target.with_suffix(".m3u")); print("Playlist criada:", target.with_suffix(".m3u")); pause()
            continue
        try:
            index = int(cmd)
            target = Path("..") if index == 0 else entries[index - 1]
        except (ValueError, IndexError):
            continue
        target = (current / target).resolve()
        if target.is_dir(): current = target
        elif target.exists(): save_history(target); play(target)


def main() -> int:
    parser = argparse.ArgumentParser(description="eazy 3.0 — navegador multimídia para Windows")
    parser.add_argument("path", nargs="?", default=".", help="diretório ou arquivo inicial")
    parser.add_argument("--version", action="version", version=f"eazy Windows {VERSION}")
    parser.add_argument("--search", metavar="TERMO", help="pesquisa rápida no diretório atual")
    parser.add_argument("--duplicates", action="store_true", help="encontra duplicados no diretório atual")
    args = parser.parse_args()
    ensure_dirs(); start = Path(args.path).expanduser().resolve()
    if args.search:
        for item in search_files(start if start.is_dir() else start.parent, name=args.search): print(item)
        return 0
    if args.duplicates:
        groups = duplicate_scan(start if start.is_dir() else start.parent)
        for i, group in enumerate(groups, 1): print(f"\nGrupo {i}:\n" + "\n".join(f"  {p}" for p in group))
        return 0
    if start.is_file(): play(start); return 0
    browser(start if start.is_dir() else Path.home()); return 0


if __name__ == "__main__":
    raise SystemExit(main())
