#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
BIN_SRC="$ROOT_DIR/bin/eazy-linux-x86_64"
EDITOR_SRC="$ROOT_DIR/eazy-notes-editor"
MAN_SRC="$ROOT_DIR/eazy.1"
DESKTOP_SRC="$ROOT_DIR/eazy.desktop"

if [[ "$(id -u)" -ne 0 ]]; then
  exec sudo "$0" "$@"
fi

for required in "$BIN_SRC" "$EDITOR_SRC" "$MAN_SRC" "$DESKTOP_SRC"; do
  if [[ ! -f "$required" ]]; then
    echo "Erro: arquivo ausente: $required" >&2
    exit 1
  fi
done

if ! file "$BIN_SRC" | grep -q 'ELF 64-bit'; then
  echo "Erro: o binário não é um executável Linux 64 bits válido." >&2
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y bash fzf whiptail mpv ffmpeg curl wget python3 ca-certificates

# Reinstalação: substitui os arquivos do programa, sem desinstalar e sem apagar configurações.
install -Dm755 "$BIN_SRC" /usr/bin/eazy
install -Dm755 "$BIN_SRC" /usr/lib/eazy/eazy
install -Dm755 "$EDITOR_SRC" /usr/lib/eazy/eazy-notes-editor
install -Dm644 "$MAN_SRC" /usr/share/man/man1/eazy.1
install -Dm644 "$DESKTOP_SRC" /usr/share/applications/eazy.desktop

if command -v mandb >/dev/null 2>&1; then
  mandb -q 2>/dev/null || true
fi

# Mantém os dados do usuário intactos e apenas garante que o diretório exista.
TARGET_HOME="${HOME:-/root}"
if [[ -n "${SUDO_USER:-}" ]]; then
  TARGET_HOME="$(getent passwd "$SUDO_USER" | cut -d: -f6)"
fi
TARGET_HOME="${TARGET_HOME:-/root}"
install -d -m 700 "$TARGET_HOME/.config/eazy"

hash -r 2>/dev/null || true
printf '\nReinstalação completa do Eazy 3.13 concluída.\n'
printf 'Binário: /usr/bin/eazy\n'
printf 'Man page: man eazy\n'
printf 'Configurações preservadas em: %s\n' "$TARGET_HOME/.config/eazy"
printf '\nVersão instalada:\n'
/usr/bin/eazy --version || true
