#!/usr/bin/env python3
"""Converte caminhos em playlists M3U entre Linux/WSL e Windows.

Uso automático (detecta pelas barras e cria arquivo com sufixo):
  python convert_m3u_paths.py auto teste.m3u

Modos explícitos:
  python convert_m3u_paths.py linux-to-windows entrada.m3u -o saida.m3u
  python convert_m3u_paths.py windows-to-linux entrada.m3u -o saida.m3u

No automático, caminhos com '/' são convertidos para Windows e geram
<nome>-linux-win.m3u; caminhos com '\\' são convertidos para Linux e geram
<nome>-win-linux.m3u. Linhas M3U iniciadas por # são preservadas.
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path


def to_windows(line: str, distro: str) -> str:
    s = line.strip()
    m = re.match(r"^/mnt/([a-zA-Z])(?:/(.*))?$", s)
    if m:
        rest = (m.group(2) or "").replace("/", "\\")
        return m.group(1).upper() + ":\\" + rest if rest else m.group(1).upper() + ":\\"
    if s.startswith("/"):
        return "\\\\wsl.localhost\\" + distro + "\\" + s.lstrip("/").replace("/", "\\")
    return line


def to_linux(line: str, distro: str) -> str:
    s = line.strip()
    unc = re.match(r"^\\\\(?:wsl\.localhost|wsl\$)\\([^\\]+)\\(.*)$", s, re.IGNORECASE)
    if unc:
        unc_distro, rest = unc.group(1), unc.group(2)
        if unc_distro.casefold() != distro.casefold():
            return line
        return "/" + rest.replace("\\", "/")
    drive = re.match(r"^([a-zA-Z]):[\\/](.*)$", s)
    if drive:
        rest = drive.group(2).replace("\\", "/")
        return "/mnt/" + drive.group(1).lower() + ("/" + rest if rest else "")
    return line


def detect_direction(text: str) -> str:
    paths = [line.strip() for line in text.splitlines()
             if line.strip() and not line.lstrip().startswith("#")
             and not line.strip().lower().startswith(("http://", "https://"))]
    has_forward = any("/" in path for path in paths)
    has_back = any("\\" in path for path in paths)
    if has_forward and has_back:
        raise ValueError("A playlist contém caminhos com os dois tipos de barra; informe o sentido explicitamente.")
    if has_forward:
        return "linux-to-windows"
    if has_back:
        return "windows-to-linux"
    raise ValueError("Não encontrei caminhos com '/' ou '\\' para detectar o sentido.")


def convert_playlist(text: str, direction: str, distro: str) -> str:
    converter = to_windows if direction == "linux-to-windows" else to_linux
    out = []
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            out.append(line)
        else:
            out.append(converter(line, distro))
    return "\n".join(out) + ("\n" if text.endswith(("\n", "\r")) else "")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("direction", choices=["auto", "linux-to-windows", "windows-to-linux"])
    parser.add_argument("input", help="Playlist M3U/M3U8 de entrada")
    parser.add_argument("-o", "--output", help="Arquivo de saída; no modo auto, o nome é gerado automaticamente")
    parser.add_argument("--windows-output-dir", help="Pasta de saída para caminhos convertidos para Windows")
    parser.add_argument("--linux-output-dir", help="Pasta de saída para caminhos convertidos para Linux")
    parser.add_argument("--detect-only", action="store_true", help="Detecta a direção e não grava arquivo")
    parser.add_argument("--distro", default="Ubuntu", help="Nome da distro WSL (padrão: Ubuntu)")
    parser.add_argument("--encoding", default="utf-8-sig", help="Codificação de entrada (padrão: utf-8-sig)")
    args = parser.parse_args()
    source = Path(args.input)
    try:
        text = source.read_text(encoding=args.encoding)
        direction = detect_direction(text) if args.direction == "auto" else args.direction
    except (OSError, UnicodeError, ValueError) as exc:
        parser.error(str(exc))
    if args.detect_only:
        print(direction)
        return
    result = convert_playlist(text, direction, args.distro)
    output = args.output
    if not output and (args.direction == "auto" or args.windows_output_dir or args.linux_output_dir):
        suffix = "-linux-win" if direction == "linux-to-windows" else "-win-linux"
        selected_dir = args.windows_output_dir if direction == "linux-to-windows" else args.linux_output_dir
        output_dir = Path(selected_dir) if selected_dir else source.parent
        if not output_dir.is_dir():
            parser.error(f"A pasta de saída não existe ou não é uma pasta: {output_dir}")
        candidate = output_dir / (source.stem + suffix + source.suffix)
        index = 2
        while candidate.exists():
            candidate = output_dir / f"{source.stem}{suffix}-{index}{source.suffix}"
            index += 1
        output = str(candidate)
    if output:
        Path(output).write_text(result, encoding="utf-8-sig", newline="")
        print(f"Conversão concluída: {output}")
    else:
        sys.stdout.write(result)


if __name__ == "__main__":
    main()
