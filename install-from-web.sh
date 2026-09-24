#!/usr/bin/env bash
# eazy 4.2.1 — branch main (fora de Releases)
set -euo pipefail
RAW="https://raw.githubusercontent.com/vapesmadcat-blip/Easy_Player/main"
TMP="${TMPDIR:-/tmp}/eazy-421-$$"
mkdir -p "$TMP" && cd "$TMP"
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

echo "==> eazy 4.2.1 do main..."
# 1) deb em dist/
if curl -fsSL -o eazy_4.2.1_all.deb "$RAW/dist/eazy_4.2.1_all.deb" 2>/dev/null; then
  echo "OK dist/eazy_4.2.1_all.deb"
# 2) zip em dist/
elif curl -fsSL -o full.zip "$RAW/dist/eazy_4.2.1_full.zip" 2>/dev/null; then
  echo "OK zip; extraindo deb..."
  command -v unzip >/dev/null && unzip -qo full.zip
  DEB=$(find . -name 'eazy_4.2.1_all.deb' | head -1)
  [ -n "$DEB" ] && cp "$DEB" eazy_4.2.1_all.deb
# 3) partes base64
elif curl -fsSL -o p0 "$RAW/dist/deb.b64.000" 2>/dev/null; then
  echo "OK partes b64..."
  cat p0 > all.b64
  for i in $(seq -f '%03g' 1 30); do
    curl -fsSL -o "p$i" "$RAW/dist/deb.b64.$i" 2>/dev/null || break
    cat "p$i" >> all.b64
  done
  base64 -d < all.b64 > eazy_4.2.1_all.deb
else
  echo "Deb 4.2.1 ainda não está no main/dist/." >&2
  echo "Fallback: última release 4.1.6" >&2
  curl -fsSL -o eazy_4.1.6_all.deb \
    "https://github.com/vapesmadcat-blip/Easy_Player/releases/download/eazy-v4.1.6/eazy_4.1.6_all.deb"
  sudo dpkg -i eazy_4.1.6_all.deb || sudo apt-get install -f -y
  exit 0
fi

curl -fsSL -o eazy_4.2.1_all.deb.sha256 "$RAW/eazy_4.2.1_all.deb.sha256" 2>/dev/null || true
[ -f eazy_4.2.1_all.deb.sha256 ] && sha256sum -c eazy_4.2.1_all.deb.sha256 || true
echo "==> dpkg..."
sudo dpkg -i eazy_4.2.1_all.deb || sudo apt-get install -f -y
eazy --version 2>/dev/null || true
