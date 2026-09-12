#!/usr/bin/env bash
# Aplica eazy-3.2.3.patch sobre ./eazy
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
TARGET="${1:-eazy}"
PATCH="eazy-3.2.3.patch"
[ -f "$TARGET" ] || { echo "Falta $TARGET"; exit 1; }
[ -f "$PATCH" ] || { echo "Falta $PATCH"; exit 1; }
cp -f -- "$TARGET" "${TARGET}.bak.$(date +%Y%m%d%H%M%S)"
patch -p0 -i "$PATCH" --forward || patch -p0 -i "$PATCH"
chmod +x "$TARGET"
bash -n "$TARGET"
"$TARGET" --version
echo "OK — recursos 3.2.3 aplicados em $TARGET"
