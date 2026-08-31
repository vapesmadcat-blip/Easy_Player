#!/usr/bin/env bash
set -euo pipefail

src="$(cd -- "$(dirname -- "$0")" && pwd -P)/eazy"
test_dir=$(mktemp -d)
lib=$(mktemp)
trap 'rm -f "$lib"; rm -rf "$test_dir"' EXIT

# Carrega somente as funções de navegação/listagem/seleção; o loop interativo não é executado.
{
    sed -n '2145,2273p' "$src"
    sed -n '4603,4620p' "$src"
    sed -n '4626,4747p' "$src"
} > "$lib"

mkdir -p "$test_dir/A/sub" "$test_dir/B"
touch "$test_dir/A/a.mp4" "$test_dir/A/b.mp4" "$test_dir/A/sub/c.mp4" "$test_dir/B/d.mp4"
cd "$test_dir/A"

SELECTED_FILE="$test_dir/selected"
LISTA_FZF_FILE="$test_dir/lista"
export SELECTED_FILE LISTA_FZF_FILE
printf '%s\n' \
    $'000000000000000\t📁 ..\t[-- MB]\t..' \
    $'000000000000001\t🎬 a.mp4\t[0.0 MB]\t./a.mp4' \
    $'000000000000002\t🎬 b.mp4\t[0.0 MB]\t./b.mp4' \
    $'000000000000003\t📁 sub/\t[-- MB]\t./sub' \
    $'000000000000004\t🎬 c.mp4\t[0.0 MB]\t./sub/c.mp4' > "$LISTA_FZF_FILE"
printf '%s\n' "$test_dir/B/d.mp4" > "$SELECTED_FILE"

source "$lib"

eazy_selection_select_all_current
[ "$(grep -c '^' "$SELECTED_FILE")" -eq 3 ]
grep -Fxq "$test_dir/A/a.mp4" "$SELECTED_FILE"
grep -Fxq "$test_dir/A/b.mp4" "$SELECTED_FILE"
grep -Fxq "$test_dir/B/d.mp4" "$SELECTED_FILE"
! grep -Fxq "$test_dir/A/sub/c.mp4" "$SELECTED_FILE"

# Ctrl-X equivalente local: remove somente a pasta em foco e preserva a seleção global externa.
eazy_selection_clear_current
[ "$(grep -c '^' "$SELECTED_FILE")" -eq 1 ]
grep -Fxq "$test_dir/B/d.mp4" "$SELECTED_FILE"

# Ctrl-R equivalente local: adiciona os dois arquivos diretos, sem descer em subpastas.
eazy_selection_invert_current
[ "$(grep -c '^' "$SELECTED_FILE")" -eq 3 ]
! grep -Fxq "$test_dir/A/sub/c.mp4" "$SELECTED_FILE"

# Tab/Espaço equivalente: alterna um único caminho sem duplicar linhas.
eazy_selection_toggle_path $'0\t🎬 a.mp4\t[0.0 MB]\t./a.mp4'
[ "$(grep -c '^' "$SELECTED_FILE")" -eq 2 ]
! grep -Fxq "$test_dir/A/a.mp4" "$SELECTED_FILE"
eazy_selection_toggle_path $'0\t🎬 a.mp4\t[0.0 MB]\t./a.mp4'
[ "$(grep -c '^' "$SELECTED_FILE")" -eq 3 ]
[ "$(sort "$SELECTED_FILE" | uniq | wc -l)" -eq 3 ]

# A linha .. nunca entra na seleção.
eazy_selection_toggle_path $'0\t📁 ..\t[-- MB]\t..'
[ "$(grep -c '^' "$SELECTED_FILE")" -eq 3 ]

# Com filtro, Ctrl-A deve atuar apenas no resultado direto correspondente.
: > "$SELECTED_FILE"
printf '%s\n' "$test_dir/B/d.mp4" > "$SELECTED_FILE"
eazy_selection_select_all_current "a.mp4"
[ "$(grep -c '^' "$SELECTED_FILE")" -eq 2 ]
grep -Fxq "$test_dir/A/a.mp4" "$SELECTED_FILE"
grep -Fxq "$test_dir/B/d.mp4" "$SELECTED_FILE"
! grep -Fxq "$test_dir/A/b.mp4" "$SELECTED_FILE"

# A filtragem mostra a marca global e mantém a linha de navegação.
filtered=$(eazy_lista_filtrada "a.mp4")
grep -Fq $'\t🎬 ✓ ' <<< "$filtered" || grep -Fq '✓ ' <<< "$filtered"
grep -Fq $'\t📁 ..' <<< "$filtered"

# Contratos estáticos do loop principal.
grep -Fq 'tecla" = "alt-enter"' "$src"
grep -Fq 'escolha=$(cat "$SELECTED_FILE"' "$src"
grep -Fq 'Enter ignora a seleção acumulada' "$src"
grep -Fq 'CTRL_A_BIND' "$src"
grep -Fq 'eazy_selection_select_all_current' "$src"

echo 'global-selection: OK'
