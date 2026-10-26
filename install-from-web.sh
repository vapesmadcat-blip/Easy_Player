#!/usr/bin/env bash
set -euo pipefail
VERSION="5.0.0"
TAG="v${VERSION}"
BASE="https://github.com/vapesmadcat-blip/Easy_Player/releases/download/${TAG}"
TMP="${TMPDIR:-/tmp}/eazy-${VERSION}-$$"
mkdir -p "$TMP"
trap 'rm -rf "$TMP"' EXIT
cd "$TMP"
printf '==> Baixando Easy %s...\n' "$VERSION"
curl -fL -o "eazy_${VERSION}_all.deb" "$BASE/eazy_${VERSION}_all.deb"
curl -fL -o "eazy_${VERSION}_all.deb.sha256" "$BASE/eazy_${VERSION}_all.deb.sha256"
sha256sum -c "eazy_${VERSION}_all.deb.sha256"
printf '==> Instalando Easy %s...\n' "$VERSION"
sudo dpkg -i "eazy_${VERSION}_all.deb" || sudo apt-get install -f -y
printf '==> Easy %s instalado.\n' "$VERSION"
eazy --version 2>/dev/null || true
