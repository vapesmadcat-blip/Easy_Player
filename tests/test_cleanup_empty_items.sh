#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"
TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/eazy-cleanup-test.XXXXXX")"
trap 'rm -rf -- "$TMP_ROOT"' EXIT
EAZY_TMP_DIR="$TMP_ROOT/tmp"
mkdir -p "$EAZY_TMP_DIR"
DRY_RUN=1
CYAN='' NC='' YELLOW=''
CAPTURED="$TMP_ROOT/listed-items"

source <(sed -n '/^listar_dirs_sem_arquivos() {/,/^}/p' "$ROOT/eazy")
source <(sed -n '/^limpar_vazios() {/,/^}/p' "$ROOT/eazy")

whiptail() { return 0; }
sleep() { :; }
fzf() {
    cat > "$CAPTURED"
    cat "$CAPTURED"
}
fail() { printf 'FAIL: %s\n' "$*" >&2; exit 1; }

base="$TMP_ROOT/root with spaces"
mkdir -p "$base/empty parent/nested empty" "$base/has zero files" "$base/nonempty dir" "$base/symlink only"
printf 'keep this content' > "$base/nonempty dir/keep.txt"
printf 'target content' > "$TMP_ROOT/symlink target"
ln -s -- "$TMP_ROOT/symlink target" "$base/symlink only/ref"
: > "$base/has zero files/zero.mp4"
: > "$base/has zero files/zero-no-extension"

# A seleção automatizada simula o usuário escolhendo todos os itens listados.
limpar_vazios "$base" >/dev/null
[ -d "$base/empty parent/nested empty" ] || fail 'DRY-RUN removeu um diretório'
[ -f "$base/has zero files/zero.mp4" ] || fail 'DRY-RUN removeu um arquivo'

DRY_RUN=0
limpar_vazios "$base" >/dev/null

[ -d "$base" ] || fail 'a pasta raiz fornecida foi incluída e removida'
[ ! -e "$base/empty parent" ] || fail 'diretórios vazios encadeados não foram removidos, ou a ordem falhou'
[ ! -e "$base/has zero files/zero.mp4" ] || fail 'arquivo 0 B com extensão não foi removido'
[ ! -e "$base/has zero files/zero-no-extension" ] || fail 'arquivo 0 B sem extensão não foi removido'
[ -f "$base/nonempty dir/keep.txt" ] || fail 'arquivo não vazio foi alterado'
[ -d "$base/nonempty dir" ] || fail 'diretório com conteúdo foi removido'
[ -L "$base/symlink only/ref" ] || fail 'symlink dentro da pasta foi removido'
[ -d "$base/symlink only" ] || fail 'diretório que contém symlink foi removido'
if grep -Fxq "[DIR] $base" "$CAPTURED"; then
    fail 'a própria raiz apareceu na lista removível'
fi
grep -F "[DIR] $base/empty parent" "$CAPTURED" >/dev/null || fail 'diretório com espaços não foi listado corretamente'
grep -F "[FILE 0B] $base/has zero files/zero.mp4" "$CAPTURED" >/dev/null || fail 'arquivo 0 B com extensão não foi listado'
if grep -F "[DIR] $base/symlink only" "$CAPTURED"; then
    fail 'diretório que contém symlink foi oferecido como vazio'
fi
printf 'OK: limpeza remove dirs vazios e arquivos regulares 0 B, preserva a raiz e conteúdo não vazio.\n'
