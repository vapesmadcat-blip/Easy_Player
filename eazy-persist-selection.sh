#!/usr/bin/env bash
# eazy-persist-selection.sh
# Module to persist selection per-folder for eazy (by folder hash).
# Minimal integration: overrides cd to save/load selection on directory changes
# and saves selection on EXIT. Designed to be sourced by the eazy runner.

# Ensure CONFIG_DIR is defined
CONFIG_DIR="${CONFIG_DIR:-${XDG_CONFIG_HOME:-$HOME/.config}/eazy}"
SELECTED_FILE="${SELECTED_FILE:-$CONFIG_DIR/selected}"

mkdir -p "$CONFIG_DIR" 2>/dev/null || true

# Helper: caminho_absoluto fallback if main script doesn't provide
caminho_absoluto_fallback() {
    local p="$1"
    if [ -z "$p" ]; then
        pwd -P
        return
    fi
    # try readlink -f, then python fallback
    if command -v readlink >/dev/null 2>&1; then
        readlink -f -- "$p" 2>/dev/null && return
    fi
    if command -v python3 >/dev/null 2>&1; then
        python3 -c "import os,sys; print(os.path.abspath(sys.argv[1]))" -- "$p" 2>/dev/null && return
    fi
    # naive fallback
    (cd -- "$(dirname -- "$p")" 2>/dev/null && printf '%s/%s' "$(pwd -P)" "$(basename -- "$p")")
}

selection_store_file_for_dir() {
    local dir="${1:-$(pwd -P)}" hash out
    mkdir -p "$CONFIG_DIR" 2>/dev/null || true
    if command -v sha1sum >/dev/null 2>&1; then
        hash=$(printf '%s' "$dir" | sha1sum 2>/dev/null | cut -d' ' -f1)
    else
        hash=$(printf '%s' "$dir" | cksum | awk '{print $1}')
    fi
    out="$CONFIG_DIR/selection_${hash}.list"
    printf '%s' "$out"
}

carregar_selecao_persistente() {
    local dir="${1:-$(pwd -P)}" file tmp
    file=$(selection_store_file_for_dir "$dir")
    # ensure SELECTED_FILE exists
    mkdir -p "$(dirname -- "$SELECTED_FILE")" 2>/dev/null || true
    : > "$SELECTED_FILE"
    [ -f "$file" ] || return 0
    tmp="${SELECTED_FILE}.tmp"
    while IFS= read -r p; do
        [ -z "$p" ] && continue
        # only add if exists
        if [ -e "$p" ]; then
            # normalize path: use main caminho_absoluto if exists
            if declare -f caminho_absoluto >/dev/null 2>&1; then
                caminho_absoluto "$p"
            else
                caminho_absoluto_fallback "$p"
            fi
        fi
    done < "$file" | sort -u > "$tmp" 2>/dev/null || :
    mv -f "$tmp" "$SELECTED_FILE" 2>/dev/null || true
}

salvar_selecao_persistente() {
    local dir="${1:-$(pwd -P)}" file tmp
    file=$(selection_store_file_for_dir "$dir")
    mkdir -p "$CONFIG_DIR" 2>/dev/null || true
    tmp="${file}.tmp"
    touch "$SELECTED_FILE" 2>/dev/null || true
    # write uniques
    sort -u "$SELECTED_FILE" 2>/dev/null > "$tmp" || : > "$tmp"
    mv -f "$tmp" "$file" 2>/dev/null || true
}

limpar_selecao_persistente() {
    local dir="${1:-$(pwd -P)}" file
    file=$(selection_store_file_for_dir "$dir")
    [ -f "$file" ] && rm -f -- "$file"
}

# Override cd to save/load selection on directory change. This intercepts plain 'cd' calls.
cd() {
    # save current selection
    local prev
    prev="$(pwd -P)"
    if declare -f salvar_selecao_persistente >/dev/null 2>&1; then
        salvar_selecao_persistente "$prev" 2>/dev/null || true
    fi
    # perform directory change using builtin cd
    builtin cd "$@" || return $?
    # load selection for new dir
    if declare -f carregar_selecao_persistente >/dev/null 2>&1; then
        carregar_selecao_persistente "$(pwd -P)" 2>/dev/null || true
    fi
}

# On exit, persist selection of current directory
_eazy_persist_on_exit() {
    if declare -f salvar_selecao_persistente >/dev/null 2>&1; then
        salvar_selecao_persistente "$(pwd -P)" 2>/dev/null || true
    fi
}

# Only set trap if not already set by main script
if ! trap -p EXIT | grep -q _eazy_persist_on_exit 2>/dev/null; then
    trap _eazy_persist_on_exit EXIT
fi

# helper commands for interactive testing
eazy_persist_save() { salvar_selecao_persistente "${1:-$(pwd -P)}"; }
eazy_persist_load() { carregar_selecao_persistente "${1:-$(pwd -P)}"; }
eazy_persist_clear() { limpar_selecao_persistente "${1:-$(pwd -P)}"; }
