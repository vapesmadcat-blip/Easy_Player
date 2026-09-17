#!/usr/bin/env bash
set -euo pipefail

REPO="vapesmadcat-blip/Easy_Player"
VERSION="3.2.12"
ASSET="eazy_${VERSION}_all.deb"
URL="https://github.com/${REPO}/releases/download/eazy-v${VERSION}/${ASSET}"
TMP_DIR="$(mktemp -d)"
DEB_PATH="${TMP_DIR}/${ASSET}"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

if [[ "${EUID}" -eq 0 ]]; then
  SUDO=""
else
  SUDO="sudo"
fi

echo "Baixando eazy ${VERSION}..."
if command -v curl >/dev/null 2>&1; then
  curl -fL --retry 3 --connect-timeout 15 -o "$DEB_PATH" "$URL"
elif command -v wget >/dev/null 2>&1; then
  wget -O "$DEB_PATH" "$URL"
else
  echo "Erro: instale curl ou wget e tente novamente." >&2
  exit 1
fi

echo "Instalando eazy ${VERSION}..."
$SUDO dpkg -i "$DEB_PATH" || {
  echo "Corrigindo dependências..."
  $SUDO apt-get update
  $SUDO apt-get -f install -y
}

echo
echo "eazy ${VERSION} instalado com sucesso."
echo "Execute: eazy"

echo "Documentação: /usr/share/doc/eazy/README.md"
