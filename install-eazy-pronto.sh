#!/usr/bin/env bash
# Instalação local do Easy 5.2.0 rev.56 beta sem sudo.
# Baixa todos os componentes primeiro e só então os instala em ~/.local/bin.
set -euo pipefail

VERSION="5.2.0"
REVISION="56"
BASE="https://raw.githubusercontent.com/vapesmadcat-blip/Easy_Player/main"
BIN="${HOME}/.local/bin"
TMP="$(mktemp -d "${TMPDIR:-/tmp}/eazy-install.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

files=(
  eazy
  eazy-index.py
  eazy-convert-m3u.py
  eazy-live-watch.py
  full.c
  migrate_eazy_lists.py
  eazy-yt-stream
  eazy-ai.py
  eazy-tor
  eazy-notes-editor
)

for file in "${files[@]}"; do
  echo ">> Baixando $file ${VERSION} rev.${REVISION}..."
  curl --fail --location --retry 3 --silent --show-error "$BASE/$file" -o "$TMP/$file"
done

chmod 755 "$TMP/eazy"
installed_version="$("$TMP/eazy" --version 2>&1)"
if ! grep -qF "${VERSION} rev.${REVISION}" <<<"$installed_version"; then
  printf 'Erro: versão inesperada no script baixado: %s\n' "$installed_version" >&2
  exit 1
fi

mkdir -p "$BIN"
for file in "${files[@]}"; do
  mode=755
  [[ "$file" == "full.c" ]] && mode=644
  install -m "$mode" "$TMP/$file" "$BIN/$file"
done

grep -qF 'export PATH="$HOME/.local/bin:$PATH"' "$HOME/.bashrc" 2>/dev/null || \
  printf '\nexport PATH="$HOME/.local/bin:$PATH"\n' >> "$HOME/.bashrc"
export PATH="$BIN:$PATH"

echo
echo "OK: $($BIN/eazy --version)"
echo "Auxiliares rev.${REVISION}: indexador, conversor M3U e monitor recursivo instalados em $BIN."
if ! command -v cc >/dev/null 2>&1 && ! command -v gcc >/dev/null 2>&1; then
  echo "Aviso: cc/gcc não encontrado; o monitor recursivo requer um compilador C para ser ativado."
fi
echo "Stream: $BIN/eazy-yt-stream"
echo
echo 'Se o PATH ainda não estiver atualizado nesta sessão:'
echo '  export PATH="$HOME/.local/bin:$PATH"'
echo '  eazy --stream'
