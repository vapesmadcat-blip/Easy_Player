#!/usr/bin/env bash
set -euo pipefail

VERSION="3.2.12"
PACKAGE="eazy_${VERSION}_all.deb"
URL="https://github.com/vapesmadcat-blip/Easy_Player/releases/download/eazy-v${VERSION}/${PACKAGE}"
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/eazy"
CONFIG_FILE="$CONFIG_DIR/ai.env"
TMP_DIR="$(mktemp -d)"
DEB_FILE="$TMP_DIR/$PACKAGE"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

if [[ "${EUID}" -eq 0 ]]; then
  SUDO=""
else
  SUDO="sudo"
fi

if ! command -v curl >/dev/null 2>&1 && ! command -v wget >/dev/null 2>&1; then
  echo "Erro: instale curl ou wget antes de continuar." >&2
  exit 1
fi

printf 'Cole sua chave OpenRouter (não será exibida): '
IFS= read -r -s API_KEY
echo
if [[ -z "$API_KEY" ]]; then
  echo "Erro: nenhuma chave foi informada." >&2
  exit 1
fi

mkdir -p "$CONFIG_DIR"
printf 'EAZY_AI_API_KEY=%s\n' "$API_KEY" > "$CONFIG_FILE"
unset API_KEY
chmod 600 "$CONFIG_FILE"

echo "Baixando eazy $VERSION com IA..."
if command -v curl >/dev/null 2>&1; then
  curl -fL --retry 3 --connect-timeout 15 -o "$DEB_FILE" "$URL"
else
  wget -O "$DEB_FILE" "$URL"
fi

echo "Instalando eazy..."
$SUDO apt-get install -y "$DEB_FILE"

chmod 600 "$CONFIG_FILE"
echo
echo "eazy $VERSION com IA instalado."
echo "Chave salva com segurança em: $CONFIG_FILE"
echo "Teste com: eazy --ai"
