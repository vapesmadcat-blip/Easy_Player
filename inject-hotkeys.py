#!/usr/bin/env python3
"""Injeta Hotkeys (F9), Ctrl+Espaco/F6, eazy --restore-keys."""
import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8", errors="replace")

def fix_alt_enter(t):
    t = t.replace(
        ' --bind="ctrl-enter:execute-silent(touch -- $EAZY_ALT_ENTER_FILE)+accept"',
        "",
    )
    old_alt = 'FZF_ALT_ENTER_BIND=(--bind="alt-enter:execute-silent(touch -- $EAZY_ALT_ENTER_FILE)+accept")'
    new_alt = (
        "FZF_ALT_ENTER_BIND=("
        '--bind="alt-enter:execute-silent(touch -- $EAZY_ALT_ENTER_FILE)+accept" '
        '--bind="ctrl-space:execute-silent(touch -- $EAZY_ALT_ENTER_FILE)+accept" '
        '--bind="f6:execute-silent(touch -- $EAZY_ALT_ENTER_FILE)+accept"'
        ")"
    )
    if old_alt in t:
        t = t.replace(old_alt, new_alt)
    elif "ctrl-space:execute-silent" not in t and "alt-enter:execute-silent" in t:
        t = t.replace(
            '--bind="alt-enter:execute-silent(touch -- $EAZY_ALT_ENTER_FILE)+accept"',
            '--bind="alt-enter:execute-silent(touch -- $EAZY_ALT_ENTER_FILE)+accept" '
            '--bind="ctrl-space:execute-silent(touch -- $EAZY_ALT_ENTER_FILE)+accept" '
            '--bind="f6:execute-silent(touch -- $EAZY_ALT_ENTER_FILE)+accept"',
        )
    t = t.replace(
        "  Alt+Enter          Executar a seleção inteira (persistente + marcas)",
        "  Ctrl+Espaço / F6   Seleção inteira (Alt+Enter se o terminal permitir)",
    )
    t = t.replace(
        "  Alt+Enter      Seleção inteira (persistente)",
        "  Ctrl+Espaço/F6 Seleção inteira",
    )
    if "Ctrl+Espaço" not in t:
        t = t.replace(
            "  Enter              Tocar só o item sob o cursor / entrar na pasta\n",
            "  Enter              Tocar só o item sob o cursor / entrar na pasta\n"
            "  Ctrl+Espaço / F6   Seleção inteira (recomendado; Alt+Enter depende do terminal)\n",
        )
    return t

def fix_restore_keys(t):
    if '[ "$1" = "--restore-keys" ]' in t:
        return t
    version_block = (
        'elif [ "$1" = "--version" ] || [ "$1" = "-V" ]; then\n'
        '    echo "${EAZY_NAME} ${EAZY_VERSION} (${EAZY_CODENAME})"\n'
        '    exit 0\n'
        'elif [ "$1" = "--config" ]; then'
    )
    restore_block = (
        'elif [ "$1" = "--version" ] || [ "$1" = "-V" ]; then\n'
        '    echo "${EAZY_NAME} ${EAZY_VERSION} (${EAZY_CODENAME})"\n'
        '    exit 0\n'
        'elif [ "$1" = "--restore-keys" ]; then\n'
        '    mkdir -p "${CONFIG_DIR:-$HOME/.config/eazy}" 2>/dev/null || true\n'
        '    if type eazy_keys_set_defaults >/dev/null 2>&1; then\n'
        '        unset KEY_SEARCH KEY_DUPES KEY_QUEUES KEY_PLAYLIST KEY_HISTORY KEY_DOWNLOADS\n'
        '        unset KEY_ACTIONS KEY_GOTO KEY_NOTES KEY_SAVE KEY_COPY KEY_MOVE KEY_EXPORT\n'
        '        unset KEY_PREVIEW KEY_CONFIG KEY_HELP KEY_QUIT KEY_QUIT2 KEY_INSERT KEY_DELETE KEY_DELETE_DISK\n'
        '        eazy_keys_set_defaults\n'
        '        eazy_keys_save\n'
        '        echo "Atalhos restaurados em: ${KEYS_FILE:-$HOME/.config/eazy/keys}"\n'
        '        echo "  F9=config | Ctrl+Espaço/F6=seleção inteira"\n'
        '    else\n'
        '        rm -f "${KEYS_FILE:-$HOME/.config/eazy/keys}" 2>/dev/null || true\n'
        '        echo "Arquivo de teclas removido (padrões na próxima abertura)."\n'
        '    fi\n'
        '    exit 0\n'
        'elif [ "$1" = "--config" ]; then'
    )
    if version_block not in t:
        print("ERRO: bloco --version/--config", file=sys.stderr)
        sys.exit(1)
    t = t.replace(version_block, restore_block, 1)
    t = t.replace(
        "  --config           Assistente de configuração (player, volume, pastas…)\n",
        "  --config           Assistente de configuração (player, volume, pastas…)\n"
        "  --restore-keys     Restaura atalhos de teclado padrão (~/.config/eazy/keys)\n",
    )
    return t

def fix_f9_hotkeys_item(t):
    if '"hotkeys"' in t and 'hotkeys) configurar_hotkeys' in t:
        return t
    if '"hotkeys"' not in t:
        t2, n = re.subn(
            r'("config"\s+"Configurar o eazy"\s*\\\n)(\s*"overview")',
            r'\1        "hotkeys" "Hotkeys — config completa de atalhos" \\\n\2',
            t,
            count=1,
        )
        if n:
            t = t2
        else:
            t = t.replace(
                '        "config" "Configurar o eazy" \\\n        "overview"',
                '        "config" "Configurar o eazy" \\\n        "hotkeys" "Hotkeys — config completa de atalhos" \\\n        "overview"',
                1,
            )
        t = t.replace('--menu "Escolha uma opção:" 16 78 4', '--menu "Escolha uma opção:" 18 78 5', 1)
    if 'hotkeys) configurar_hotkeys' not in t:
        t = t.replace(
            '        sound) testar_som; return ;;\n        config) : ;;',
            '        sound) testar_som; return ;;\n        hotkeys) configurar_hotkeys; return ;;\n        config) : ;;',
            1,
        )
    return t

_has_hotkeys = "configurar_hotkeys()" in text
if _has_hotkeys:
    print("Hotkeys já presentes — aplicando fixes")
    text = fix_alt_enter(text)
    text = fix_restore_keys(text)
    text = fix_f9_hotkeys_item(text)
    path.write_text(text, encoding="utf-8")
    print("OK fixes (Ctrl+Espaço/F6 + --restore-keys + F9)")
    sys.exit(0)

if "KEYS_FILE=" not in text:
    text = text.replace(
        'CONFIG_FILE="$CONFIG_DIR/config"\n',
        'CONFIG_FILE="$CONFIG_DIR/config"\nKEYS_FILE="$CONFIG_DIR/keys"\n',
        1,
    )

keys_block = r"""
# --- Hotkeys (F9 → Hotkeys) ---
eazy_keys_set_defaults() {
    KEY_SEARCH="${KEY_SEARCH:-ctrl-f}"
    KEY_DUPES="${KEY_DUPES:-ctrl-d}"
    KEY_QUEUES="${KEY_QUEUES:-ctrl-p}"
    KEY_PLAYLIST="${KEY_PLAYLIST:-ctrl-o}"
    KEY_HISTORY="${KEY_HISTORY:-ctrl-g}"
    KEY_DOWNLOADS="${KEY_DOWNLOADS:-ctrl-b}"
    KEY_ACTIONS="${KEY_ACTIONS:-ctrl-k}"
    KEY_GOTO="${KEY_GOTO:-ctrl-l}"
    KEY_NOTES="${KEY_NOTES:-ctrl-n}"
    KEY_SAVE="${KEY_SAVE:-ctrl-s}"
    KEY_COPY="${KEY_COPY:-ctrl-y}"
    KEY_MOVE="${KEY_MOVE:-ctrl-u}"
    KEY_EXPORT="${KEY_EXPORT:-ctrl-e}"
    KEY_PREVIEW="${KEY_PREVIEW:-ctrl-/}"
    KEY_CONFIG="${KEY_CONFIG:-f9}"
    KEY_HELP="${KEY_HELP:-f10}"
    KEY_QUIT="${KEY_QUIT:-q}"
    KEY_QUIT2="${KEY_QUIT2:-ctrl-q}"
    KEY_INSERT="${KEY_INSERT:-insert}"
    KEY_DELETE="${KEY_DELETE:-del}"
    KEY_DELETE_DISK="${KEY_DELETE_DISK:-alt-d}"
}
eazy_keys_set_defaults
if [ -f "${KEYS_FILE:-}" ]; then
    # shellcheck disable=SC1090
    source "$KEYS_FILE" 2>/dev/null || true
    eazy_keys_set_defaults
fi
eazy_keys_save() {
    mkdir -p "$CONFIG_DIR" 2>/dev/null || true
    cat > "$KEYS_FILE" <<EOF
KEY_SEARCH="$KEY_SEARCH"
KEY_DUPES="$KEY_DUPES"
KEY_QUEUES="$KEY_QUEUES"
KEY_PLAYLIST="$KEY_PLAYLIST"
KEY_HISTORY="$KEY_HISTORY"
KEY_DOWNLOADS="$KEY_DOWNLOADS"
KEY_ACTIONS="$KEY_ACTIONS"
KEY_GOTO="$KEY_GOTO"
KEY_NOTES="$KEY_NOTES"
KEY_SAVE="$KEY_SAVE"
KEY_COPY="$KEY_COPY"
KEY_MOVE="$KEY_MOVE"
KEY_EXPORT="$KEY_EXPORT"
KEY_PREVIEW="$KEY_PREVIEW"
KEY_CONFIG="$KEY_CONFIG"
KEY_HELP="$KEY_HELP"
KEY_QUIT="$KEY_QUIT"
KEY_QUIT2="$KEY_QUIT2"
KEY_INSERT="$KEY_INSERT"
KEY_DELETE="$KEY_DELETE"
KEY_DELETE_DISK="$KEY_DELETE_DISK"
EOF
}
eazy_normalize_tecla() {
    local t="${1:-}"
    case "$t" in
        "$KEY_SEARCH") echo "ctrl-f" ;;
        "$KEY_DUPES") echo "ctrl-d" ;;
        "$KEY_QUEUES") echo "ctrl-p" ;;
        "$KEY_PLAYLIST") echo "ctrl-o" ;;
        "$KEY_HISTORY") echo "ctrl-g" ;;
        "$KEY_DOWNLOADS") echo "ctrl-b" ;;
        "$KEY_ACTIONS") echo "ctrl-k" ;;
        "$KEY_GOTO") echo "ctrl-l" ;;
        "$KEY_NOTES") echo "ctrl-n" ;;
        "$KEY_SAVE") echo "ctrl-s" ;;
        "$KEY_COPY") echo "ctrl-y" ;;
        "$KEY_MOVE") echo "ctrl-u" ;;
        "$KEY_EXPORT") echo "ctrl-e" ;;
        "$KEY_PREVIEW"|"ctrl-_") echo "ctrl-/" ;;
        "$KEY_CONFIG") echo "f9" ;;
        "$KEY_HELP") echo "f10" ;;
        "$KEY_QUIT") echo "q" ;;
        "$KEY_QUIT2") echo "ctrl-q" ;;
        "$KEY_INSERT") echo "insert" ;;
        "$KEY_DELETE") echo "del" ;;
        "$KEY_DELETE_DISK") echo "alt-d" ;;
        *) echo "$t" ;;
    esac
}

"""

m = 'if [ -f "$CONFIG_FILE" ]; then\n    source "$CONFIG_FILE"\nfi\n'
if "eazy_keys_set_defaults" not in text:
    if m not in text:
        print("ERRO: CONFIG_FILE source", file=sys.stderr)
        sys.exit(1)
    text = text.replace(m, m + keys_block, 1)

fn = r"""
configurar_hotkeys() {
    mkdir -p "$CONFIG_DIR" 2>/dev/null || true
    eazy_keys_set_defaults
    while true; do
        local escolha
        escolha=$(whiptail --title "Hotkeys — configuração completa" \
            --menu "Ação → tecla (fzf: ctrl-j, f8, alt-s)\nSeleção inteira fixa: Ctrl+Espaço / F6\nEmergência: eazy --restore-keys" 22 78 14 \
            "search"     "Busca              [$KEY_SEARCH]" \
            "dupes"      "Duplicados         [$KEY_DUPES]" \
            "queues"     "Filas              [$KEY_QUEUES]" \
            "playlist"   "Playlist           [$KEY_PLAYLIST]" \
            "history"    "Histórico          [$KEY_HISTORY]" \
            "downloads"  "Downloads          [$KEY_DOWNLOADS]" \
            "actions"    "Ações              [$KEY_ACTIONS]" \
            "goto"       "Ir à pasta         [$KEY_GOTO]" \
            "notes"      "Notas              [$KEY_NOTES]" \
            "save"       "Salvar             [$KEY_SAVE]" \
            "copy"       "Copiar             [$KEY_COPY]" \
            "move"       "Mover              [$KEY_MOVE]" \
            "export"     "Shuffle/export     [$KEY_EXPORT]" \
            "preview"    "Preview            [$KEY_PREVIEW]" \
            "config"     "Abrir F9           [$KEY_CONFIG]" \
            "help"       "Ajuda              [$KEY_HELP]" \
            "quit"       "Sair               [$KEY_QUIT]" \
            "quit2"      "Sair alt           [$KEY_QUIT2]" \
            "insert"     "Insert             [$KEY_INSERT]" \
            "delete"     "Apagar             [$KEY_DELETE]" \
            "deldisk"    "Apagar disco       [$KEY_DELETE_DISK]" \
            "reset"      "Restaurar padrões (como --restore-keys)" \
            "done"       "Salvar e voltar" \
            3>&1 1>&2 2>&3) || return 0
        case "$escolha" in
            done)
                eazy_keys_save
                whiptail --title "Hotkeys" --msgbox "Salvo em:\n$KEYS_FILE\n\nSe travar os atalhos:\neazy --restore-keys" 12 55
                return 0
                ;;
            reset)
                unset KEY_SEARCH KEY_DUPES KEY_QUEUES KEY_PLAYLIST KEY_HISTORY KEY_DOWNLOADS
                unset KEY_ACTIONS KEY_GOTO KEY_NOTES KEY_SAVE KEY_COPY KEY_MOVE KEY_EXPORT
                unset KEY_PREVIEW KEY_CONFIG KEY_HELP KEY_QUIT KEY_QUIT2 KEY_INSERT KEY_DELETE KEY_DELETE_DISK
                eazy_keys_set_defaults
                eazy_keys_save
                whiptail --title "Hotkeys" --msgbox "Padrões restaurados.\n(igual a: eazy --restore-keys)" 10 45
                ;;
            search|dupes|queues|playlist|history|downloads|actions|goto|notes|save|copy|move|export|preview|config|help|quit|quit2|insert|delete|deldisk)
                local var cur label
                case "$escolha" in
                    search) var=KEY_SEARCH; cur="$KEY_SEARCH"; label="Busca" ;;
                    dupes) var=KEY_DUPES; cur="$KEY_DUPES"; label="Duplicados" ;;
                    queues) var=KEY_QUEUES; cur="$KEY_QUEUES"; label="Filas" ;;
                    playlist) var=KEY_PLAYLIST; cur="$KEY_PLAYLIST"; label="Playlist" ;;
                    history) var=KEY_HISTORY; cur="$KEY_HISTORY"; label="Histórico" ;;
                    downloads) var=KEY_DOWNLOADS; cur="$KEY_DOWNLOADS"; label="Downloads" ;;
                    actions) var=KEY_ACTIONS; cur="$KEY_ACTIONS"; label="Ações" ;;
                    goto) var=KEY_GOTO; cur="$KEY_GOTO"; label="Ir à pasta" ;;
                    notes) var=KEY_NOTES; cur="$KEY_NOTES"; label="Notas" ;;
                    save) var=KEY_SAVE; cur="$KEY_SAVE"; label="Salvar" ;;
                    copy) var=KEY_COPY; cur="$KEY_COPY"; label="Copiar" ;;
                    move) var=KEY_MOVE; cur="$KEY_MOVE"; label="Mover" ;;
                    export) var=KEY_EXPORT; cur="$KEY_EXPORT"; label="Shuffle/export" ;;
                    preview) var=KEY_PREVIEW; cur="$KEY_PREVIEW"; label="Preview" ;;
                    config) var=KEY_CONFIG; cur="$KEY_CONFIG"; label="Abrir F9" ;;
                    help) var=KEY_HELP; cur="$KEY_HELP"; label="Ajuda" ;;
                    quit) var=KEY_QUIT; cur="$KEY_QUIT"; label="Sair" ;;
                    quit2) var=KEY_QUIT2; cur="$KEY_QUIT2"; label="Sair alt" ;;
                    insert) var=KEY_INSERT; cur="$KEY_INSERT"; label="Insert" ;;
                    delete) var=KEY_DELETE; cur="$KEY_DELETE"; label="Apagar" ;;
                    deldisk) var=KEY_DELETE_DISK; cur="$KEY_DELETE_DISK"; label="Apagar disco" ;;
                esac
                local novo
                novo=$(whiptail --title "Hotkey: $label" \
                    --inputbox "Tecla fzf (ex.: ctrl-j, f8, alt-s)\nAtual: $cur\n\nSeleção inteira fixa: Ctrl+Espaço e F6" 13 55 "$cur" \
                    3>&1 1>&2 2>&3) || continue
                novo=$(echo "$novo" | tr '[:upper:]' '[:lower:]' | tr -d ' \t')
                [ -z "$novo" ] && continue
                eval "$var=\"\$novo\""
                ;;
        esac
    done
}

"""
if "configurar_hotkeys()" not in text:
    text = text.replace("configurar_defaults() {", fn + "configurar_defaults() {", 1)

old = (
    '    f9_acao=$(whiptail --title "F9 — Configuração e diagnóstico" \\\n'
    '        --menu "Escolha uma opção:" 16 78 4 \\\n'
    '        "config" "Configurar o eazy" \\\n'
    '        "overview" "Overview do sistema" \\\n'
    '        "sound" "Teste de som" \\\n'
    '        "cancel" "Voltar" \\\n'
    '        3>&1 1>&2 2>&3)\n'
    '    case "$f9_acao" in\n'
    '        overview) mostrar_overview_sistema_completo; return ;;\n'
    '        sound) testar_som; return ;;\n'
    '        config) : ;;\n'
    '        *) return 0 ;;\n'
    '    esac'
)

new = (
    '    f9_acao=$(whiptail --title "F9 — Configuração e diagnóstico" \\\n'
    '        --menu "Escolha uma opção:" 18 78 5 \\\n'
    '        "config" "Configurar o eazy" \\\n'
    '        "hotkeys" "Hotkeys — config completa de atalhos" \\\n'
    '        "overview" "Overview do sistema" \\\n'
    '        "sound" "Teste de som" \\\n'
    '        "cancel" "Voltar" \\\n'
    '        3>&1 1>&2 2>&3)\n'
    '    case "$f9_acao" in\n'
    '        overview) mostrar_overview_sistema_completo; return ;;\n'
    '        sound) testar_som; return ;;\n'
    '        hotkeys) configurar_hotkeys; return ;;\n'
    '        config) : ;;\n'
    '        *) return 0 ;;\n'
    '    esac'
)

if old in text:
    text = text.replace(old, new, 1)
else:
    print("ERRO: menu F9", file=sys.stderr)
    sys.exit(1)

old_e = (
    '    FZF_EXPECT="f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,ctrl-h,del,alt-d,alt-x,insert,ctrl-s,ctrl-o,ctrl-f,ctrl-p,ctrl-d,ctrl-b,ctrl-n,ctrl-q,ctrl-y,ctrl-u,ctrl-g,ctrl-e,ctrl-k,ctrl-l,${EAZY_FZF_BACKSPACE_EXPECT}ctrl-/,q,X"\n'
    '    if [ "${MODO_DUP:-0}" -ne 1 ]; then\n'
    '        FZF_EXPECT="f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,ctrl-h,del,alt-d,alt-x,insert,ctrl-s,ctrl-o,ctrl-f,ctrl-p,ctrl-d,ctrl-b,ctrl-n,ctrl-t,ctrl-q,ctrl-y,ctrl-u,ctrl-g,ctrl-e,ctrl-k,ctrl-l,${EAZY_FZF_BACKSPACE_EXPECT}ctrl-/,q,X"\n'
    '    fi'
)

new_e = (
    '    eazy_keys_set_defaults\n'
    '    FZF_EXPECT="f1,f2,f3,f4,f5,f6,f7,f8,f12,ctrl-h,alt-x,${EAZY_FZF_BACKSPACE_EXPECT}X"\n'
    '    for _k in "$KEY_DELETE" "$KEY_DELETE_DISK" "$KEY_INSERT" "$KEY_SAVE" "$KEY_PLAYLIST" \\\n'
    '              "$KEY_SEARCH" "$KEY_QUEUES" "$KEY_DUPES" "$KEY_DOWNLOADS" "$KEY_NOTES" \\\n'
    '              "$KEY_QUIT2" "$KEY_COPY" "$KEY_MOVE" "$KEY_HISTORY" "$KEY_EXPORT" \\\n'
    '              "$KEY_ACTIONS" "$KEY_GOTO" "$KEY_PREVIEW" "$KEY_CONFIG" "$KEY_HELP" "$KEY_QUIT"; do\n'
    '        [ -n "$_k" ] && FZF_EXPECT="${FZF_EXPECT},${_k}"\n'
    '    done\n'
    '    if [ "${MODO_DUP:-0}" -ne 1 ]; then\n'
    '        FZF_EXPECT="${FZF_EXPECT},ctrl-t"\n'
    '    fi\n'
    "    FZF_EXPECT=$(echo \"$FZF_EXPECT\" | tr ',' '\\n' | awk 'NF && !seen[$0]++' | paste -sd, -)\n"
)

if old_e in text:
    text = text.replace(old_e, new_e, 1)
else:
    print("ERRO: FZF_EXPECT", file=sys.stderr)
    sys.exit(1)

if 'eazy_normalize_tecla "$tecla"' not in text:
    idx = text.find("tecla=$(printf")
    if idx < 0:
        print("ERRO: tecla=", file=sys.stderr)
        sys.exit(1)
    le = text.find("\n", idx)
    text = text[:le] + '\n    tecla=$(eazy_normalize_tecla "$tecla")' + text[le:]

text = fix_alt_enter(text)
text = fix_restore_keys(text)
text = fix_f9_hotkeys_item(text)

if not text.startswith("#!"):
    text = "#!/usr/bin/env bash\n" + text

path.write_text(text, encoding="utf-8")
print("OK Hotkeys + Ctrl+Espaço/F6 + --restore-keys + F9")
