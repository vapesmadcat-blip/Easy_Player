#!/usr/bin/env bash
set -euo pipefail
VER="${EAZY_VERSION:-4.2.1}"
REPO="vapesmadcat-blip/Easy_Player"
TAG="eazy-v${VER}"
BASE="https://github.com/${REPO}/releases/download/${TAG}"
DEB="eazy_${VER}_all.deb"
TMP="${TMPDIR:-/tmp}/eazy-install-$$"
mkdir -p "$TMP"
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT
echo "==> Baixando ${DEB} (${TAG})..."
curl -fsSL -o "$TMP/$DEB" "${BASE}/${DEB}"
curl -fsSL -o "$TMP/${DEB}.sha256" "${BASE}/${DEB}.sha256" 2>/dev/null || true
if [ -f "$TMP/${DEB}.sha256" ]; then
  (cd "$TMP" && sha256sum -c "${DEB}.sha256") || true
fi
echo "==> Instalando..."
sudo dpkg -i "$TMP/$DEB" || sudo apt-get install -f -y
eazy --version 2>/dev/null || true
