#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
LIB="$TMP/lib.sh"
python3 - "$ROOT/eazy" "$LIB" <<'PY'
from pathlib import Path
import sys
src = Path(sys.argv[1]).read_text()
out = Path(sys.argv[2])
start = src.index('caminho_absoluto() {')
end = src.index('# --- Editor de notas rápidas ---', start)
caminho = src[start:end]
start = src.index('eazy_selection_sync_current() {')
end = src.index('export -f eazy_lista_filtrada', start)
selection = src[start:end]
out.write_text(caminho + selection)
PY
mkdir -p "$TMP/A" "$TMP/B"
touch "$TMP/A/a.mp4" "$TMP/A/b.mp4" "$TMP/A/c.mp4" "$TMP/B/out.mp3"
SELECTED_FILE="$TMP/selected"
SELECTION_VISIBLE_FILE="$TMP/visible"
LISTA_FZF_FILE="$TMP/lista"
export SELECTED_FILE SELECTION_VISIBLE_FILE LISTA_FZF_FILE
printf '%s\n' "$TMP/B/out.mp3" > "$SELECTED_FILE"
printf '%s\n' \
  $'0\t🎬 a.mp4\t[0 MB]\t./a.mp4' \
  $'1\t🎬 b.mp4\t[0 MB]\t./b.mp4' \
  $'2\t🎬 c.mp4\t[0 MB]\t./c.mp4' > "$LISTA_FZF_FILE"
cp "$LISTA_FZF_FILE" "$SELECTION_VISIBLE_FILE"
cd "$TMP/A"
source "$LIB"
eazy_selection_sync_current "$(sed -n '1p' "$LISTA_FZF_FILE")" "$(sed -n '2p' "$LISTA_FZF_FILE")"
[ "$(wc -l < "$SELECTED_FILE")" -eq 3 ]
grep -Fxq "$TMP/A/a.mp4" "$SELECTED_FILE"
grep -Fxq "$TMP/A/b.mp4" "$SELECTED_FILE"
grep -Fxq "$TMP/B/out.mp3" "$SELECTED_FILE"
# Desmarcar tudo no diretório atual preserva o item externo.
eazy_selection_sync_current
[ "$(wc -l < "$SELECTED_FILE")" -eq 1 ]
grep -Fxq "$TMP/B/out.mp3" "$SELECTED_FILE"
# Com filtro, somente o item visível é substituído; os ocultos permanecem.
printf '%s\n' $'0\t🎬 a.mp4\t[0 MB]\t./a.mp4' > "$SELECTION_VISIBLE_FILE"
printf '%s\n' "$TMP/A/a.mp4" "$TMP/A/b.mp4" "$TMP/B/out.mp3" > "$SELECTED_FILE"
eazy_selection_sync_current
[ "$(wc -l < "$SELECTED_FILE")" -eq 2 ]
grep -Fxq "$TMP/A/b.mp4" "$SELECTED_FILE"
grep -Fxq "$TMP/B/out.mp3" "$SELECTED_FILE"
# Repetições não geram duplicidades.
eazy_selection_sync_current "$(sed -n '1p' "$LISTA_FZF_FILE")" "$(sed -n '1p' "$LISTA_FZF_FILE")"
[ "$(sort "$SELECTED_FILE" | uniq -d | wc -l)" -eq 0 ]
echo 'selection-persistence: OK'
