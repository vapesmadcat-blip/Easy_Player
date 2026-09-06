#!/usr/bin/env bash
set -euo pipefail

src="$(cd -- "$(dirname -- "$0")" && pwd -P)/eazy"
test_dir=$(mktemp -d)
lib=$(mktemp)
trap 'rm -f "$lib"; rm -rf "$test_dir"' EXIT

# Carrega as duas funções reais sob teste, sem iniciar o loop interativo.
{
    sed -n '3050,3064p' "$src"
    sed -n '3205,3308p' "$src"
} > "$lib"

mkdir -p "$test_dir/A/sub" "$test_dir/B"
touch "$test_dir/A/a.mp4" "$test_dir/A/b.mp4" "$test_dir/A/sub/c.mp4" "$test_dir/B/d.mp4"
cd "$test_dir/A"

SELECTED_FILE="$test_dir/selected"
SELECTED_DIRS_FILE="$test_dir/selected.dirs"
SELECTED_LOCAL_FILE="$test_dir/selected.local"
LISTA_FZF_FILE="$test_dir/lista"
FZF_QUERY="a.mp4"
export SELECTED_FILE SELECTED_DIRS_FILE SELECTED_LOCAL_FILE LISTA_FZF_FILE FZF_QUERY
: > "$SELECTED_FILE"
: > "$SELECTED_DIRS_FILE"
: > "$SELECTED_LOCAL_FILE"
printf '%s\n' \
    $'000000000000000\t📁 ..\t[-- MB]\t..' \
    $'000000000000001\t🎬 a.mp4\t[0.0 MB]\t./a.mp4' \
    $'000000000000002\t🎬 b.mp4\t[0.0 MB]\t./b.mp4' \
    $'000000000000003\t📁 sub/\t[-- MB]\t./sub' \
    $'000000000000004\t🎬 c.mp4\t[0.0 MB]\t./sub/c.mp4' > "$LISTA_FZF_FILE"
printf '%s\n' "$test_dir/B/d.mp4" > "$SELECTED_FILE"

caminho_absoluto() {
    local p="$1"
    if [[ "$p" = /* ]]; then printf '%s\n' "$p"; else readlink -f -- "$p"; fi
}
arquivo_selecao_global() {
    local linha="$1" p
    p=$(printf '%s\n' "$linha" | awk -F '\\t' '{print $NF}')
    [ -n "$p" ] || return 1
    [[ "$p" == ".." ]] && return 1
    caminho_absoluto "$p"
}
adicionar_selecao_global() {
    local p="$1"
    [ -f "$p" ] || return 0
    grep -Fxq -- "$p" "$SELECTED_FILE" 2>/dev/null || printf '%s\n' "$p" >> "$SELECTED_FILE"
}
expandir_diretorio_selecao() {
    local dir="$1" p
    find "$dir" -type f -print0 2>/dev/null | while IFS= read -r -d '' p; do
        adicionar_selecao_global "$p"
    done
}
BUSCA_CACHE_DIR=""
DUP_SELECTED_FILE=""
DUP_FIXED_FILE=""
DUP_MANUAL_FILE=""
source "$lib"
eazy_select_visible_global "$FZF_QUERY"

[ "$(grep -c '^' "$SELECTED_FILE")" -eq 2 ]
grep -Fxq "$test_dir/A/a.mp4" "$SELECTED_FILE"
grep -Fxq "$test_dir/B/d.mp4" "$SELECTED_FILE"
! grep -Fxq "$test_dir/A/b.mp4" "$SELECTED_FILE"
! grep -Fxq "$test_dir/A/sub/c.mp4" "$SELECTED_FILE"

echo 'ctrl-a-filter: OK'
