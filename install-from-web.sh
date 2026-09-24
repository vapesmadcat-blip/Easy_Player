#!/usr/bin/env bash
# Instala eazy 4.1.1 a partir do GitHub Releases
set -euo pipefail
VER="${EAZY_VERSION:-4.1.1}"
REPO="vapesmadcat-blip/Easy_Player"
TAG="v${VER}"
BASE="https://github.com/${REPO}/releases/download/${TAG}"
DEB="eazy_${VER}_all.deb"
TMP="${TMPDIR:-/tmp}/eazy-install-$$"
mkdir -p "$TMP"
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

echo "==> Baixando ${DEB} (${TAG})..."
if command -v curl >/dev/null 2>&1; then
  curl -fsSL -o "$TMP/$DEB" "${BASE}/${DEB}"
  curl -fsSL -o "$TMP/${DEB}.sha256" "${BASE}/${DEB}.sha256" 2>/dev/null || true
elif command -v wget >/dev/null 2>&1; then
  wget -q -O "$TMP/$DEB" "${BASE}/${DEB}"
  wget -q -O "$TMP/${DEB}.sha256" "${BASE}/${DEB}.sha256" 2>/dev/null || true
else
  echo "Instale curl ou wget." >&2; exit 1
fi

if [ -f "$TMP/${DEB}.sha256" ]; then
  echo "==> Verificando SHA256..."
  (cd "$TMP" && sha256sum -c "${DEB}.sha256")
fi

echo "==> Instalando (dpkg)..."
sudo dpkg -i "$TMP/$DEB" || sudo apt-get install -f -y
echo "==> OK. Rode: eazy --version"
eazy --version 2>/dev/null || true
