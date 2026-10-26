#!/usr/bin/env bash
# Instalação local do Easy 5.0.0 sem sudo.
# Os componentes ficam juntos em ~/.local/bin para que o stream seja encontrado pelo eazy.
set -euo pipefail
VERSION="5.0.0"
BASE="https://raw.githubusercontent.com/vapesmadcat-blip/Easy_Player/main"
BIN="${HOME}/.local/bin"
mkdir -p "$BIN"
for file in eazy eazy-yt-stream eazy-ai.py eazy-tor eazy-notes-editor; do
  echo ">> Baixando $file $VERSION..."
  curl -fsSL "$BASE/$file" -o "$BIN/$file"
  chmod 755 "$BIN/$file"
done
grep -qF 'export PATH="$HOME/.local/bin:$PATH"' "$HOME/.bashrc" 2>/dev/null || \
  printf '\nexport PATH="$HOME/.local/bin:$PATH"\n' >> "$HOME/.bashrc"
export PATH="$BIN:$PATH"
echo
echo "OK: $($BIN/eazy --version)"
echo "Stream: $BIN/eazy-yt-stream"
echo
echo 'Se o PATH ainda não estiver atualizado nesta sessão:'
echo '  export PATH="$HOME/.local/bin:$PATH"'
echo '  eazy --stream'
