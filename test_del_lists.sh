#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
LIB="$TMP/delete-functions.sh"
awk '/^confirmar_e_excluir\(\) \{/{on=1} on{print} /^# --- Compactar seleção/{exit}' "$ROOT/eazy" > "$LIB"
# A função só precisa destes valores no ramo de listas.
EAZY_TMP_DIR="$TMP/eazy-tmp"
mkdir -p "$EAZY_TMP_DIR"
export EAZY_TMP_DIR
source "$LIB"

# Download: URL com regex e remoção do último item precisam persistir.
DOWNLOAD_QUEUE="$TMP/download_queue"
printf '%s\n' \
  'aria|https://example.test/video?a=1[2]|senha' \
  'wget|https://example.test/outro|-' > "$DOWNLOAD_QUEUE"
export DOWNLOAD_QUEUE MODO_DOWNLOAD=1
printf 's\n' | confirmar_e_excluir $'\t📥 item\t[Senha]\thttps://example.test/video?a=1[2]'
grep -Fxq 'wget|https://example.test/outro|-' "$DOWNLOAD_QUEUE"
! grep -Fq 'video?a=1[2]' "$DOWNLOAD_QUEUE"
printf 's\n' | confirmar_e_excluir $'\t📥 item\t[Senha]\thttps://example.test/outro'
[ ! -s "$DOWNLOAD_QUEUE" ]

# Playlist: DEL altera o arquivo real, não apenas a lista exibida.
PLAYLIST="$TMP/temp_playlist_1"
printf '%s\n' '/media/um.mp4' '/media/dois.mp4' > "$PLAYLIST"
ARQUIVO_PLAYLIST_ABERTO="$PLAYLIST"
MODO_DOWNLOAD=0
MODO_PLAYLIST=1
export ARQUIVO_PLAYLIST_ABERTO MODO_DOWNLOAD MODO_PLAYLIST
printf 's\n' | confirmar_e_excluir $'\t🎬 um.mp4\t[1 MB]\t/media/um.mp4'
grep -Fxq '/media/dois.mp4' "$PLAYLIST"
! grep -Fq '/media/um.mp4' "$PLAYLIST"
printf 'del-lists: OK\n'
