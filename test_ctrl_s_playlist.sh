#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
TMP_TEST=$(mktemp -d)
trap 'rm -rf "$TMP_TEST"' EXIT

awk '/^salvar_playlist\(\) \{/{on=1} on{print} /^confirmar_e_excluir\(\) \{/{exit}' "$ROOT/eazy" | sed '$d' > "$TMP_TEST/function.sh"

MOCK_COUNT_FILE="$TMP_TEST/mock-count"
whiptail() {
    if [[ "$*" == *"--inputbox"* ]]; then
        if [ ! -e "$MOCK_COUNT_FILE" ]; then
            : > "$MOCK_COUNT_FILE"
            printf '%s\n' "$TMP_TEST/out" >&3
        else
            printf '%s\n' "playlist.m3u" >&3
        fi
    fi
    return 0
}

caminho_absoluto() { printf '%s\n' "$1"; }
export HOME="$TMP_TEST/home"
CONFIG_DIR="$TMP_TEST/config"
PLAYLIST_DIR_PADRAO="$TMP_TEST/out"
PLAYLIST_FILE="$CONFIG_DIR/temp_playlist_1"
ARQUIVO_PLAYLIST_ABERTO="$CONFIG_DIR/temp_playlist_custom_musicas"
mkdir -p "$CONFIG_DIR" "$PLAYLIST_DIR_PADRAO"
printf '%s\n' '/tmp/da-fila-1.mp3' > "$PLAYLIST_FILE"
printf '%s\n' '/tmp/da-lista-atual.mp3' > "$ARQUIVO_PLAYLIST_ABERTO"
MODO_PLAYLIST=1
FILA_ATUAL=1

source "$TMP_TEST/function.sh"
salvar_playlist

test -f "$PLAYLIST_DIR_PADRAO/playlist.m3u"
grep -q '/tmp/da-lista-atual.mp3' "$PLAYLIST_DIR_PADRAO/playlist.m3u"
! grep -q '/tmp/da-fila-1.mp3' "$PLAYLIST_DIR_PADRAO/playlist.m3u"
printf 'OK: Ctrl-S salvou a lista temporária atualmente aberta.\n'
