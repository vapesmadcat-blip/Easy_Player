#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"
TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/eazy-selection-scope.XXXXXX")"
trap 'rm -rf -- "$TMP_ROOT"' EXIT
EAZY_INDEXER="$ROOT/eazy-index.py"
EAZY_INDEX_DB="$TMP_ROOT/index.sqlite3"
PYTHON_CMD=python3
EAZY_SQL_SELECTION=1
EAZY_IGNORE=0
MODO_PLAYLIST=0 MODO_DOWNLOAD=0 MODO_DUP=0 MODO_BUSCA=0
TEST_CHOICE=local
DIALOG_LOG="$TMP_ROOT/dialog.log"
mkdir -p "$TMP_ROOT/visible" "$TMP_ROOT/elsewhere"
printf local > "$TMP_ROOT/visible/yellow.txt"
printf global > "$TMP_ROOT/elsewhere/global.txt"
python3 "$EAZY_INDEXER" --db "$EAZY_INDEX_DB" --init >/dev/null
python3 "$EAZY_INDEXER" --db "$EAZY_INDEX_DB" --selection-set "$TMP_ROOT/visible/yellow.txt" 1 >/dev/null
python3 "$EAZY_INDEXER" --db "$EAZY_INDEX_DB" --selection-set "$TMP_ROOT/elsewhere/global.txt" 2 >/dev/null
source <(sed -n '/^# BEGIN EAZY COPY SELECTION AND PREFLIGHT$/,/^# END EAZY COPY SELECTION AND PREFLIGHT$/p' "$ROOT/eazy")
caminho_absoluto() { realpath -m -- "$1"; }
whiptail() {
    printf '%s\n' "$*" >> "$DIALOG_LOG"
    printf '%s\n' "$TEST_CHOICE" >&3
    return 0
}
fail() { printf 'FAIL: %s\n' "$*" >&2; exit 1; }

cd "$TMP_ROOT/visible"
: > "$DIALOG_LOG"
TEST_CHOICE=local
eazy_prepare_copy_move_selection Copiar ""
local_result="$EAZY_PREPARED_SELECTION"
[[ "$local_result" == "$TMP_ROOT/visible/yellow.txt"$'\n' ]] || fail "a opção local trouxe caminho inesperado: $local_result"
grep -q '1 item(ns) na seleção global' "$DIALOG_LOG" || fail 'o diálogo não mostrou a contagem global'
[ "$(python3 "$EAZY_INDEXER" --db "$EAZY_INDEX_DB" --selection-count --selection-state 1)" = 1 ] || fail 'a seleção local foi promovida ou alterada'
[ "$(python3 "$EAZY_INDEXER" --db "$EAZY_INDEX_DB" --selection-count --selection-state 2)" = 1 ] || fail 'a seleção global foi alterada'

: > "$DIALOG_LOG"
TEST_CHOICE=unir
eazy_prepare_copy_move_selection Copiar ""
union_result="$EAZY_PREPARED_SELECTION"
[[ "$union_result" == *"$TMP_ROOT/visible/yellow.txt"* ]] || fail 'a união perdeu o item amarelo'
[[ "$union_result" == *"$TMP_ROOT/elsewhere/global.txt"* ]] || fail 'a união não incluiu o item global'
[ "$(printf '%s' "$union_result" | grep -c '^')" -eq 2 ] || fail 'a união duplicou ou omitiu itens'

# Sem amarelos, um caminho global devolvido pelo FZF não pode vazar para a
# opção “somente seleção atual”.
python3 "$EAZY_INDEXER" --db "$EAZY_INDEX_DB" --selection-clear --selection-state 1 \
    --selection-root "$TMP_ROOT/visible" >/dev/null
TEST_CHOICE=local
incoming_row=$'linha\t'"$TMP_ROOT/elsewhere/global.txt"
eazy_prepare_copy_move_selection Copiar "$incoming_row"
[ -z "$EAZY_PREPARED_SELECTION" ] || fail 'a opção local incluiu silenciosamente um item global vindo do FZF'

TEST_CHOICE=""
if eazy_prepare_copy_move_selection Copiar ""; then fail 'cancelar o diálogo continuou a operação'; fi
printf 'OK: seleção local/global, contagem, união opcional, filtro e cancelamento passaram.\n'
