#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
EAZY_SOURCE="$(cd -- "$SCRIPT_DIR/.." && pwd -P)/eazy"
TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/eazy-copy-test.XXXXXX")"
trap 'rm -rf -- "$TMP_ROOT"' EXIT

source <(sed -n '/^# BEGIN EAZY COPY TREE HELPERS$/,/^# END EAZY COPY TREE HELPERS$/p' "$EAZY_SOURCE")
source <(sed -n '/^# BEGIN EAZY COPY SELECTION AND PREFLIGHT$/,/^# END EAZY COPY SELECTION AND PREFLIGHT$/p' "$EAZY_SOURCE")
source <(sed -n '/^copiar_arquivos() {/,/^}/p' "$EAZY_SOURCE")

LAST_COPY_DEST_FILE="$TMP_ROOT/last-copy-dest"
ACTION_FILE="$TMP_ROOT/actions"
PROMPT_LOG="$TMP_ROOT/prompts"
SIMULATION_LOG="$TMP_ROOT/simulation-prompts"
WHIPTAIL_LOG="$TMP_ROOT/whiptail.log"
TEST_DEST=""
EAZY_SQL_SELECTION=0
EAZY_IGNORE=1
CONFIRM_RESULT=0

caminho_absoluto() { realpath -m -- "$1"; }
escolher_destino() { printf '%s\n' "$TEST_DEST"; }
montar_detalhe_espaco() { printf 'fixture de teste\n'; }
somar_selecao_bytes() { printf '0\n'; }
verificar_espaco_disco() { return 0; }
formatar_bytes_label() { printf '%s bytes' "${1:-0}"; }
eazy_status_file() { :; }
eazy_status_file_clear() { :; }
sleep() { :; }
whiptail() {
    printf '%s\n' "$*" >> "$WHIPTAIL_LOG"
    [[ "$*" == *"--yesno"* && "$CONFIRM_RESULT" = 1 ]] && return 1
    return 0
}

# Ações são consumidas de arquivo porque a rotina do menu roda em command substitution.
eazy_copy_conflict_menu() {
    local source="$1" target="$2" choice
    if [ "${EAZY_COPY_PREFLIGHT_RUNNING:-0}" = 1 ]; then
        printf '%s -> %s\n' "$source" "$target" >> "$SIMULATION_LOG"
    else
        printf '%s -> %s\n' "$source" "$target" >> "$PROMPT_LOG"
    fi
    if [ -s "$ACTION_FILE" ]; then
        choice=$(head -n1 "$ACTION_FILE")
        tail -n +2 "$ACTION_FILE" > "$ACTION_FILE.next"
        mv -- "$ACTION_FILE.next" "$ACTION_FILE"
    else
        choice="cancel"
    fi
    printf '%s\n' "$choice"
}

fail() { printf 'FAIL: %s\n' "$*" >&2; exit 1; }
assert_file_content() {
    local path="$1" expected="$2" actual
    [ -f "$path" ] || fail "arquivo ausente: $path"
    actual=$(cat -- "$path")
    [ "$actual" = "$expected" ] || fail "conteúdo inesperado em $path: '$actual' (esperado '$expected')"
}
reset_test_state() {
    : > "$ACTION_FILE"
    : > "$PROMPT_LOG"
    : > "$SIMULATION_LOG"
    : > "$WHIPTAIL_LOG"
    CONFIRM_RESULT=0
    TEST_DEST="$TMP_ROOT/destination"
    rm -rf -- "$TEST_DEST"
    mkdir -p -- "$TEST_DEST"
    LAST_COPY_DEST_FILE="$TMP_ROOT/last-copy-dest"
    rm -f -- "$LAST_COPY_DEST_FILE"
    PREFLIGHT_CHOICE=ask
}
selection_for() {
    local p result=""
    for p in "$@"; do
        result+=$'item\t'"$p"$'\n'
    done
    printf '%s' "$result"
}

# 1) Três árvores com nomes de pasta internos iguais não se achatam nem se mesclam.
reset_test_state
src="$TMP_ROOT/source tree"
mkdir -p -- "$src/Artist one/Same name" "$src/Artist two/Same name" "$src/Artist three/Same name"
printf 'one' > "$src/Artist one/Same name/track.mp3"
printf 'two' > "$src/Artist two/Same name/track.mp3"
printf 'three' > "$src/Artist three/Same name/track.mp3"
copiar_arquivos "$(selection_for "$src/Artist one/Same name" "$src/Artist two/Same name" "$src/Artist three/Same name")"
assert_file_content "$TEST_DEST/Artist one/Same name/track.mp3" one
assert_file_content "$TEST_DEST/Artist two/Same name/track.mp3" two
assert_file_content "$TEST_DEST/Artist three/Same name/track.mp3" three
[ ! -e "$TEST_DEST/Same name" ] || fail 'árvores com basename repetido foram achatadas'

# 2) Pular um arquivo mantém o destino intacto e permite seguir com o trabalho.
reset_test_state
src="$TMP_ROOT/skip source"
mkdir -p -- "$src/branch"
printf 'new' > "$src/branch/song.mp3"
printf 'next' > "$src/branch/next.mp3"
printf 'old' > "$TEST_DEST/song.mp3"
printf 'skip\n' > "$ACTION_FILE"
copiar_arquivos "$(selection_for "$src/branch/song.mp3" "$src/branch/next.mp3")"
assert_file_content "$TEST_DEST/song.mp3" old
assert_file_content "$TEST_DEST/next.mp3" next
[ "${EAZY_COPY_SKIPPED:-0}" -eq 1 ] || fail 'o contador de pulados não foi atualizado'

# 3) Renomear é automático, preserva a extensão e nunca destrói o nome já usado.
reset_test_state
src="$TMP_ROOT/rename source"
mkdir -p -- "$src/branch"
printf 'new' > "$src/branch/song.mp3"
printf 'old' > "$TEST_DEST/song.mp3"
printf 'older copy' > "$TEST_DEST/song (cópia).mp3"
printf 'rename\n' > "$ACTION_FILE"
copiar_arquivos "$(selection_for "$src/branch/song.mp3")"
assert_file_content "$TEST_DEST/song.mp3" old
assert_file_content "$TEST_DEST/song (cópia).mp3" 'older copy'
assert_file_content "$TEST_DEST/song (cópia 2).mp3" new

# 4) Sobrescrever somente acontece depois de escolha explícita.
reset_test_state
src="$TMP_ROOT/overwrite source"
mkdir -p -- "$src/branch"
printf 'new' > "$src/branch/song.mp3"
printf 'old' > "$TEST_DEST/song.mp3"
printf 'overwrite\n' > "$ACTION_FILE"
copiar_arquivos "$(selection_for "$src/branch/song.mp3")"
assert_file_content "$TEST_DEST/song.mp3" new
[ "${EAZY_COPY_OVERWRITTEN:-0}" -eq 1 ] || fail 'o contador de sobrescritos não foi atualizado'

# 5) Pular todos os conflitos restantes pergunta uma vez e deixa ambos os originais.
reset_test_state
src="$TMP_ROOT/skip all source"
mkdir -p -- "$src/Artist A/Album" "$src/Artist B/Album"
printf 'new A' > "$src/Artist A/Album/song.mp3"
printf 'new B' > "$src/Artist B/Album/song.mp3"
mkdir -p -- "$TEST_DEST/Artist A/Album" "$TEST_DEST/Artist B/Album"
printf 'old A' > "$TEST_DEST/Artist A/Album/song.mp3"
printf 'old B' > "$TEST_DEST/Artist B/Album/song.mp3"
printf 'skip_all\n' > "$ACTION_FILE"
copiar_arquivos "$(selection_for "$src/Artist A/Album" "$src/Artist B/Album")"
assert_file_content "$TEST_DEST/Artist A/Album/song.mp3" 'old A'
assert_file_content "$TEST_DEST/Artist B/Album/song.mp3" 'old B'
[ "$(wc -l < "$SIMULATION_LOG")" -eq 1 ] || fail 'skip_all mostrou mais de um menu de simulação'
[ ! -s "$PROMPT_LOG" ] || fail 'houve pergunta de conflito durante a cópia real'

# 6) Cancelar impede o processamento dos itens ainda não copiados.
reset_test_state
src="$TMP_ROOT/cancel source"
mkdir -p -- "$src/Artist A/Album" "$src/Artist B/Album"
printf 'new A' > "$src/Artist A/Album/song.mp3"
printf 'new B' > "$src/Artist B/Album/song.mp3"
mkdir -p -- "$TEST_DEST/Artist A/Album"
printf 'old A' > "$TEST_DEST/Artist A/Album/song.mp3"
printf 'cancel\n' > "$ACTION_FILE"
copiar_arquivos "$(selection_for "$src/Artist A/Album" "$src/Artist B/Album")" || true
assert_file_content "$TEST_DEST/Artist A/Album/song.mp3" 'old A'
[ "${EAZY_COPY_PREFLIGHT_CANCEL:-0}" -eq 1 ] || fail 'o cancelamento da simulação não foi registrado'
[ ! -e "$TEST_DEST/Artist B" ] || fail 'a cópia continuou após o cancelamento'

# 7) Sobrescrever colisão de tipo pasta/arquivo respeita a escolha explícita.
reset_test_state
src="$TMP_ROOT/type source"
mkdir -p -- "$src/branch/album"
printf 'inside' > "$src/branch/album/song.mp3"
printf 'old file' > "$TEST_DEST/album"
printf 'overwrite\n' > "$ACTION_FILE"
copiar_arquivos "$(selection_for "$src/branch/album")"
assert_file_content "$TEST_DEST/album/song.mp3" inside

# 8) Marcar pasta e descendente juntos não duplica a cópia nem dispara colisão.
reset_test_state
src="$TMP_ROOT/dedup source"
mkdir -p -- "$src/Artist/Album"
printf 'track' > "$src/Artist/Album/song.mp3"
copiar_arquivos "$(selection_for "$src/Artist/Album" "$src/Artist/Album/song.mp3")"
assert_file_content "$TEST_DEST/Album/song.mp3" track
[ ! -s "$PROMPT_LOG" ] || fail 'pasta e descendente foram copiados duas vezes'

# 9) Um destino dentro da origem é recusado antes de iniciar a cópia recursiva.
reset_test_state
src="$TMP_ROOT/recursive source"
mkdir -p -- "$src/Artist/Album/output"
printf 'keep' > "$src/Artist/Album/song.mp3"
TEST_DEST="$src/Artist/Album/output"
copiar_arquivos "$(selection_for "$src/Artist/Album")"
assert_file_content "$src/Artist/Album/song.mp3" keep
[ ! -e "$TEST_DEST/Album" ] || fail 'a cópia recursiva dentro da origem não foi bloqueada'
grep -q 'Destino inválido' "$WHIPTAIL_LOG" || fail 'o usuário não foi avisado do destino dentro da origem'

# 10) Copiar a pasta para o pai dela não pode mapear a saída sobre a própria origem.
reset_test_state
src="$TMP_ROOT/self-copy source"
mkdir -p -- "$src/parent/album"
printf 'keep' > "$src/parent/album/song.mp3"
TEST_DEST="$src/parent"
copiar_arquivos "$(selection_for "$src/parent/album")"
assert_file_content "$src/parent/album/song.mp3" keep
[ "${EAZY_COPY_FAILED:-0}" -eq 1 ] || fail 'o destino igual à origem não foi recusado'
grep -q 'Destino inválido' "$WHIPTAIL_LOG" || fail 'faltou aviso para destino igual à origem'

# 11) A simulação conta conflitos e permite renomear todos antes de iniciar;
#     a rotina não abre o menu tardio por conflito.
reset_test_state
src="$TMP_ROOT/preflight rename"
mkdir -p -- "$src/branch"
printf 'new' > "$src/branch/song.mp3"
printf 'old' > "$TEST_DEST/song.mp3"
printf 'rename\n' > "$ACTION_FILE"
copiar_arquivos "$(selection_for "$src/branch/song.mp3")"
assert_file_content "$TEST_DEST/song.mp3" old
assert_file_content "$TEST_DEST/song (cópia).mp3" new
[ ! -s "$PROMPT_LOG" ] || fail 'a decisão de renomear foi pedida novamente durante a cópia'
[ "$(wc -l < "$SIMULATION_LOG")" -eq 1 ] || fail 'o conflito não foi resolvido na simulação'
grep -q 'Conflitos previstos: 1' "$WHIPTAIL_LOG" || fail 'a simulação não mostrou a colisão prevista'

# 12) Sobrescrever todos pela prévia aplica a decisão sem novo diálogo tardio.
reset_test_state
src="$TMP_ROOT/preflight overwrite"
mkdir -p -- "$src/branch"
printf 'new' > "$src/branch/song.mp3"
printf 'old' > "$TEST_DEST/song.mp3"
printf 'overwrite\n' > "$ACTION_FILE"
copiar_arquivos "$(selection_for "$src/branch/song.mp3")"
assert_file_content "$TEST_DEST/song.mp3" new
[ ! -s "$PROMPT_LOG" ] || fail 'sobrescrever foi perguntado novamente durante a cópia'

# 13) Pular um item pela prévia mantém o destino e não repete perguntas.
reset_test_state
src="$TMP_ROOT/preflight skip"
mkdir -p -- "$src/branch"
printf 'new' > "$src/branch/song.mp3"
printf 'old' > "$TEST_DEST/song.mp3"
printf 'skip\n' > "$ACTION_FILE"
copiar_arquivos "$(selection_for "$src/branch/song.mp3")"
assert_file_content "$TEST_DEST/song.mp3" old
[ "${EAZY_COPY_SKIPPED:-0}" -eq 1 ] || fail 'pular pela prévia não atualizou o contador'
[ ! -s "$PROMPT_LOG" ] || fail 'pular foi perguntado novamente durante a cópia'

# 14) Conflitos distintos recebem respostas individuais na simulação; a cópia
#     real respeita ambas sem abrir nenhum menu.
reset_test_state
src="$TMP_ROOT/preflight individual"
mkdir -p -- "$src/branch"
printf 'new one' > "$src/branch/one.mp3"
printf 'new two' > "$src/branch/two.mp3"
printf 'old one' > "$TEST_DEST/one.mp3"
printf 'old two' > "$TEST_DEST/two.mp3"
printf 'rename\noverwrite\n' > "$ACTION_FILE"
copiar_arquivos "$(selection_for "$src/branch/one.mp3" "$src/branch/two.mp3")"
assert_file_content "$TEST_DEST/one.mp3" 'old one'
assert_file_content "$TEST_DEST/one (cópia).mp3" 'new one'
assert_file_content "$TEST_DEST/two.mp3" 'new two'
[ "$(wc -l < "$SIMULATION_LOG")" -eq 2 ] || fail 'a simulação não apresentou ambos os conflitos antes de copiar'
[ ! -s "$PROMPT_LOG" ] || fail 'a cópia real ainda abriu menus de conflito'

# 15) Cancelar na simulação impede qualquer processamento.
reset_test_state
src="$TMP_ROOT/preflight cancel"
mkdir -p -- "$src/branch"
printf 'new' > "$src/branch/song.mp3"
printf 'old' > "$TEST_DEST/song.mp3"
printf 'cancel\n' > "$ACTION_FILE"
copiar_arquivos "$(selection_for "$src/branch/song.mp3")" || true
assert_file_content "$TEST_DEST/song.mp3" old

# 16) Recusar a confirmação final também impede qualquer escrita.
reset_test_state
src="$TMP_ROOT/preflight final decline"
mkdir -p -- "$src/branch"
printf 'new' > "$src/branch/song.mp3"
CONFIRM_RESULT=1
copiar_arquivos "$(selection_for "$src/branch/song.mp3")" || true
[ ! -e "$TEST_DEST/song.mp3" ] || fail 'a cópia começou apesar da recusa final'

# 17) Duplicados não usa o plano novo; mantém a confirmação antiga por conflito.
reset_test_state
src="$TMP_ROOT/duplicate mode"
mkdir -p -- "$src/branch"
printf 'new' > "$src/branch/song.mp3"
printf 'old' > "$TEST_DEST/song.mp3"
printf 'rename\n' > "$ACTION_FILE"
MODO_DUP=1
copiar_arquivos "$(selection_for "$src/branch/song.mp3")"
MODO_DUP=0
assert_file_content "$TEST_DEST/song.mp3" old
assert_file_content "$TEST_DEST/song (cópia).mp3" new
[ "$(wc -l < "$PROMPT_LOG")" -eq 1 ] || fail 'o fluxo Duplicados foi alterado pelo novo plano'
[ ! -s "$SIMULATION_LOG" ] || fail 'Duplicados entrou na simulação do navegador normal'

printf 'OK: 17 testes de cópia passaram.\n'
