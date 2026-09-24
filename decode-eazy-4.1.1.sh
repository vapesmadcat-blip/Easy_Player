#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
OUT="${1:-eazy_4.1.1_all.deb}"
cat "$DIR"/eazy_4.1.1_all.deb.b64.* | base64 -d > "$OUT"
echo "Wrote $OUT ($(wc -c < "$OUT") bytes)"
sha256sum "$OUT"
