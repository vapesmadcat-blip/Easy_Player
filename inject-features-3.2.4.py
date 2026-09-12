#!/usr/bin/env python3
"""Injeta recursos 3.2.4 no eazy. Uso: python3 inject-features-3.2.4.py eazy"""
import sys
from pathlib import Path
path = Path(sys.argv[1] if len(sys.argv) > 1 else "eazy")
t = path.read_text(encoding="utf-8", errors="replace")
for bad in ("ctrl-shift-delete", "alt-shift-delete"):
    t = t.replace("," + bad, "").replace(bad + ",", "").replace(bad, "")
FUNCS = 'eazy_prune_selecao_global() {\n    local tmp p\n    [ -f "${SELECTED_FILE:-}" ] || return 0\n    tmp="${SELECTED_FILE}.prune.tmp"\n    : > "$tmp"\n    while IFS= read -r p; do\n        [ -z "$p" ] && continue\n        [ -e "$p" ] || continue\n        printf \'%s\\n\' "$p" >> "$tmp"\n    done < "$SELECTED_FILE"\n    mv -f -- "$tmp" "$SELECTED_FILE"\n    if [ -f "${SELECTED_DIRS_FILE:-}" ]; then\n        tmp="${SELECTED_DIRS_FILE}.prune.tmp"\n        : > "$tmp"\n        while IFS= read -r p; do\n            [ -z "$p" ] && continue\n            [ -d "$p" ] || continue\n            printf \'%s\\n\' "$p" >> "$tmp"\n        done < "$SELECTED_DIRS_FILE"\n        mv -f -- "$tmp" "$SELECTED_DIRS_FILE"\n    fi\n}\n\neazy_prune_lista_arquivo() {\n    local lista="$1" tmp linha res\n    [ -n "$lista" ] && [ -f "$lista" ] || return 0\n    tmp="${lista}.prune.tmp"\n    : > "$tmp"\n    while IFS= read -r linha || [ -n "$linha" ]; do\n        linha="${linha%$\'\\r\'}"\n        if [ -z "$linha" ] || [[ "$linha" =~ ^# ]]; then\n            printf \'%s\\n\' "$linha" >> "$tmp"\n            continue\n        fi\n        res="$linha"\n        if [[ "$linha" != /* ]] && [[ ! "$linha" =~ ^https?:// ]]; then\n            res="$(dirname -- "$lista")/$linha"\n        fi\n        if [[ "$linha" =~ ^https?:// ]]; then\n            printf \'%s\\n\' "$linha" >> "$tmp"\n            continue\n        fi\n        if [ -e "$linha" ] || [ -e "$res" ]; then\n            printf \'%s\\n\' "$linha" >> "$tmp"\n        fi\n    done < "$lista"\n    mv -f -- "$tmp" "$lista"\n}\n\nabrir_lixeira() {\n    local trash="$HOME/.local/share/Trash/files"\n    if [ ! -d "$trash" ]; then\n        mkdir -p "$trash" 2>/dev/null || true\n    fi\n    if [ ! -d "$trash" ]; then\n        whiptail --title "Lixeira" --msgbox "Lixeira não encontrada:\\n$trash" 9 55\n        return 1\n    fi\n    if cd -- "$trash" 2>/dev/null; then\n        MODO_BUSCA=0; MODO_DUP=0; MODO_PLAYLIST=0; MODO_DOWNLOAD=0\n        ARQUIVO_PLAYLIST_ABERTO=""\n        FZF_QUERY=""\n        TMP=1; ALVO="$(pwd)"; ULTIMO_DIR="$(pwd)"; ULTIMO_ARQUIVO=""\n        registrar_status 2>/dev/null || true\n        return 0\n    fi\n    whiptail --title "Lixeira" --msgbox "Não foi possível entrar em:\\n$trash" 9 55\n    return 1\n}\n\nexportar_notas_eazy() {\n    local dest="$HOME/Documentos/Easy-Notes"\n    mkdir -p "$dest" "$NOTES_DIR" 2>/dev/null || true\n    local n\n    n=$(find "$NOTES_DIR" -maxdepth 1 -type f ! -name \'.*\' 2>/dev/null | wc -l)\n    n=$(echo "$n" | tr -cd \'0-9\'); n=${n:-0}\n    if [ "$n" -eq 0 ]; then\n        whiptail --title "Exportar notas" --msgbox "Nenhuma nota em:\\n$NOTES_DIR" 9 55\n        return 0\n    fi\n    if cp -a -- "$NOTES_DIR"/. "$dest"/ 2>/dev/null; then\n        whiptail --title "Exportar notas" --msgbox "Copiadas $n nota(s) para:\\n$dest" 10 60\n    else\n        whiptail --title "Exportar notas" --msgbox "Falha ao copiar para:\\n$dest" 9 55\n    fi\n}\n\neazy_filtro_label() {\n    case "${1:-}" in\n        videos) echo "videos (mp4/mkv/avi/webm/mov…)" ;;\n        audios) echo "audios (mp3/m4a/flac/wav…)" ;;\n        imgs) echo "imgs (jpg/png/gif/webp…)" ;;\n        compactados) echo "compactados (zip/7z/rar/tar…)" ;;\n        todos) echo "todos" ;;\n        ambos) echo "mídia" ;;\n        *) echo "${1:-}" ;;\n    esac\n}\n\neh_arquivo_html() {\n    local f="$1" ext\n    [ ! -f "$f" ] && return 1\n    ext=$(echo "${f##*.}" | tr \'[:upper:]\' \'[:lower:]\')\n    case "$ext" in html|htm|xhtml) return 0 ;; esac\n    return 1\n}\n\nabrir_html_ou_link() {\n    local alvo="$1"\n    if [[ "$alvo" =~ ^https?:// ]]; then\n        if command -v xdg-open >/dev/null 2>&1; then\n            xdg-open "$alvo" >/dev/null 2>&1 &\n        elif command -v sensible-browser >/dev/null 2>&1; then\n            sensible-browser "$alvo" >/dev/null 2>&1 &\n        else\n            whiptail --title "Link" --msgbox "Abra no browser:\\n$alvo" 10 70\n        fi\n        return 0\n    fi\n    if eh_arquivo_html "$alvo"; then\n        if command -v xdg-open >/dev/null 2>&1; then\n            xdg-open "$alvo" >/dev/null 2>&1 &\n        else\n            mostrar_texto "$alvo"\n        fi\n        return 0\n    fi\n    return 1\n}'

if "eazy_prune_selecao_global()" not in t:
    t = t.replace("eazy_clear_global_confirm() {", FUNCS + "\n\neazy_clear_global_confirm() {", 1)
    print("+ prune/lixeira/html/export/filtro helpers")

# F9 menu items
if '"lixeira"' not in t:
    t = t.replace(
        '        "sound" "Teste de som" \\\n        "cancel" "Voltar"',
        '        "sound" "Teste de som" \\\n        "lixeira" "Abrir lixeira do sistema" \\\n        "export_notas" "Exportar notas → Documentos/Easy-Notes" \\\n        "cancel" "Voltar"',
    )
    t = t.replace(
        "        sound) testar_som; return ;;\n",
        "        sound) testar_som; return ;;\n        lixeira) abrir_lixeira; return ;;\n        export_notas) exportar_notas_eazy; return ;;\n",
    )
    t = t.replace('--menu "Escolha uma opção:" 18 78 5', '--menu "Escolha uma opção:" 20 78 7')
    t = t.replace('--menu "Escolha uma opção:" 16 78 4', '--menu "Escolha uma opção:" 20 78 7')
    print("+ F9 lixeira/export")

# filtro label in prompt
if "eazy_filtro_label" in t and '$(eazy_filtro_label' not in t:
    t = t.replace(
        'TEXTO_PROMPT=" 📂 [$FILTRO_ATUAL] $PASTA_ATUAL ❯ "',
        'TEXTO_PROMPT=" 📂 [$(eazy_filtro_label \"$FILTRO_ATUAL\")] $PASTA_ATUAL ❯ "',
    )
    print("+ filtro label prompt")

# HTML open on enter
if "abrir_html_ou_link" in t and "elif eh_arquivo_html" not in t:
    t = t.replace(
        'elif eh_arquivo_texto "$tocado"; then\n                    mostrar_texto "$tocado"',
        'elif eh_arquivo_html "$tocado" || [[ "$tocado" =~ ^https?:// ]]; then\n                    abrir_html_ou_link "$tocado"\n                elif eh_arquivo_texto "$tocado"; then\n                    mostrar_texto "$tocado"',
    )
    t = t.replace(
        'elif eh_arquivo_texto "$ULTIMO_ARQUIVO"; then\n                mostrar_texto "$ULTIMO_ARQUIVO"',
        'elif eh_arquivo_html "$ULTIMO_ARQUIVO" || [[ "$ULTIMO_ARQUIVO" =~ ^https?:// ]]; then\n                abrir_html_ou_link "$ULTIMO_ARQUIVO"\n            elif eh_arquivo_texto "$ULTIMO_ARQUIVO"; then\n                mostrar_texto "$ULTIMO_ARQUIVO"',
    )
    print("+ HTML/link enter")

# Del = cursor only
if "somente o arquivo sob o cursor" not in t:
    old = (
        '    elif [ "$tecla" = "del" ]; then\n'
        '        # DEL: na playlist = só da lista; na tela principal = do disco\n'
        '        confirmar_e_excluir "$escolha"; continue\n'
        '    elif [ "$tecla" = "alt-d" ]; then\n'
        '        # ALT+D: apaga do DISCO (e da playlist, se estiver nela)\n'
        '        # (fzf não suporta ctrl-del de forma confiável)\n'
        '        confirmar_e_excluir "$escolha" "disco"; continue\n'
    )
    new = (
        '    elif [ "$tecla" = "del" ]; then\n'
        '        if [ -n "${cursor_raw:-}" ]; then _del_item="$cursor_raw"; else _del_item=$(printf \'%s\\n\' "$escolha" | head -n1); fi\n'
        '        confirmar_e_excluir "$_del_item"; unset _del_item; continue\n'
        '    elif [ "$tecla" = "shift-delete" ]; then\n'
        '        if [ "${MODO_DUP:-0}" -eq 1 ]; then\n'
        '            if [ ! -s "${DUP_SELECTED_FILE:-}" ]; then whiptail --title "Duplicados" --msgbox "Seleção amarela vazia." 8 50 2>/dev/null || true; continue; fi\n'
        '            confirmar_e_excluir "$(cat -- "$DUP_SELECTED_FILE")"; continue\n'
        '        fi\n'
        '        _a=$(whiptail --title "Shift+Del" --menu "Seleção?" 11 50 2 "local" "Esta tela" "global" "Global" 3>&1 1>&2 2>&3) || continue\n'
        '        if [ "$_a" = "global" ]; then\n'
        '            [ -s "${SELECTED_FILE:-}" ] || { whiptail --msgbox "Global vazia." 8 40; continue; }\n'
        '            confirmar_e_excluir "$(cat -- "$SELECTED_FILE")"\n'
        '        else\n'
        '            confirmar_e_excluir "$(printf \'%s\\n\' "$escolha" | eazy_sem_navegacao 2>/dev/null || printf \'%s\\n\' "$escolha")"\n'
        '        fi\n'
        '        continue\n'
        '    elif [ "$tecla" = "alt-d" ]; then\n'
        '        confirmar_e_excluir "$escolha" "disco"; continue\n'
    )
    if old in t:
        t = t.replace(old, new, 1)
        print("+ Del/Shift+Del")
    # FZF_EXPECT shift-delete
    needle = '    FZF_EXPECT=$(echo "$FZF_EXPECT" | tr \',\' \'\\n\' | awk \'NF && !seen[$0]++\' | paste -sd, -)\n'
    if needle in t and "shift-delete" not in t[max(0,t.find("FZF_EXPECT=$(echo")-50):t.find("FZF_EXPECT=$(echo")+500]:
        t = t.replace(needle, needle + '    case ",$FZF_EXPECT," in *,shift-delete,*) ;; *) FZF_EXPECT="${FZF_EXPECT},shift-delete" ;; esac\n', 1)
        print("+ FZF shift-delete")

# Prune after disk delete
if "eazy_prune_selecao_global" in t and "eazy_prune_selecao_global 2>/dev/null" not in t:
    for end_pat in [
        '        echo -e "\\033[1;32mConcluído.\\033[0m"\n        sleep 1\n',
        '        echo -e "\\033[1;32mApagado(s) do disco.\\033[0m"\n        sleep 1\n',
    ]:
        if end_pat in t:
            t = t.replace(end_pat, '        eazy_prune_selecao_global 2>/dev/null || true\n' + end_pat, 1)
            print("+ prune after delete")
            break

path.write_text(t)
print("OK", path)
