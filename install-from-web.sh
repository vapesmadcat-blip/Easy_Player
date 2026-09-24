#!/usr/bin/env bash
# Instala a última release PUBLICADA no GitHub
set -euo pipefail
REPO="vapesmadcat-blip/Easy_Player"
# 4.2.1 ainda não tem release/asset → default = última publicada
VER="${EAZY_VERSION:-4.1.6}"
TAG="eazy-v${VER}"
BASE="https://github.com/${REPO}/releases/download/${TAG}"
DEB="eazy_${VER}_all.deb"
TMP="${TMPDIR:-/tmp}/eazy-install-$$"
mkdir -p "$TMP"
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

echo "==> Baixando ${DEB} (${TAG})..."
if ! curl -fsSL -o "$TMP/$DEB" "${BASE}/${DEB}"; then
  echo "ERRO 404: release ${TAG} não existe ou não tem o .deb." >&2
  echo "Última publicada: eazy-v4.1.6" >&2
  echo "Liste: https://github.com/${REPO}/releases" >&2
  exit 1
fi
curl -fsSL -o "$TMP/${DEB}.sha256" "${BASE}/${DEB}.sha256" 2>/dev/null || true
if [ -f "$TMP/${DEB}.sha256" ]; then
  echo "==> Verificando SHA256..."
  (cd "$TMP" && sha256sum -c "${DEB}.sha256") || true
fi
echo "==> Instalando..."
sudo dpkg -i "$TMP/$DEB" || sudo apt-get install -f -y
echo "==> OK"
command -v eazy >/dev/null && eazy --version || true
