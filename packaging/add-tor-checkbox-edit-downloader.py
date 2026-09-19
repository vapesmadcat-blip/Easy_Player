from pathlib import Path
p=Path('/home/ubuntu/easy_player_current/eazy')
s=p.read_text()
# Queue editing: add engine selector before URL and preserve fourth field (Tor flag).
s=s.replace('''    local tmp escolhido linha engine url rest novo
''','''    local tmp escolhido linha engine url rest novo novo_engine tor_item
''',1)
s=s.replace('''    rest=$(printf "%s" "$linha" | cut -d"|" -f3-)
    novo=$(whiptail --title "Editar link download #$num" --inputbox "URL / link:\\nMotor: $engine" 12 78 "$url" 3>&1 1>&2 2>&3) || return 0
    [ -z "$novo" ] && return 0
''','''    rest=$(printf "%s" "$linha" | cut -d"|" -f3-)
    tor_item=$(printf "%s" "$linha" | cut -d"|" -f4)
    [ "$tor_item" != "1" ] && tor_item="0"
    novo_engine=$(whiptail --title "Editar downloader #$num" --radiolist "Escolha o aplicativo para este item:" 13 65 4 \\
        "aria" "aria2c" $( [ "$engine" = aria ] && echo ON || echo OFF ) \\
        "axel" "Axel" $( [ "$engine" = axel ] && echo ON || echo OFF ) \\
        "wget" "Wget" $( [ "$engine" = wget ] && echo ON || echo OFF ) \\
        "ytdlp" "yt-dlp" $( [ "$engine" = ytdlp ] && echo ON || echo OFF ) \\
        3>&1 1>&2 2>&3) || return 0
    [ -z "$novo_engine" ] && novo_engine="$engine"
    novo=$(whiptail --title "Editar link download #$num" --inputbox "URL / link:\\nMotor: $novo_engine" 12 78 "$url" 3>&1 1>&2 2>&3) || return 0
    [ -z "$novo" ] && return 0
''',1)
s=s.replace('''    awk -v n="$num" -v eng="$engine" -v u="$novo" -v r="$rest" -F"|" "
        NR==n { print eng "|" u "|" r; next }
''','''    awk -v n="$num" -v eng="$novo_engine" -v u="$novo" -v r="$rest" -v tor="$tor_item" -F"|" "
        NR==n { print eng "|" u "|" r "|" tor; next }
''',1)
# Add checkbox at end of adding flow and store as 4th queue field.
s=s.replace('''    echo "$gerenciador|$link|$extra" >> "$DOWNLOAD_QUEUE"
    whiptail --title "Sucesso" --msgbox "Adicionado à fila!\\n\\nMotor: $gerenciador" 9 45
''','''    local usar_tor="0"
    if whiptail --title "Rede Tor" --checklist "Usar Tor neste download?\\n(Tor deve estar ativo em 127.0.0.1:9050)" 10 72 1 \\
        "TOR" "SOCKS5 127.0.0.1:9050" OFF 3>&1 1>&2 2>&3 | grep -q TOR; then
        usar_tor="1"
    fi
    echo "$gerenciador|$link|$extra|$usar_tor" >> "$DOWNLOAD_QUEUE"
    whiptail --title "Sucesso" --msgbox "Adicionado à fila!\\n\\nMotor: $gerenciador\\nTor: $([ "$usar_tor" = 1 ] && echo ATIVO || echo desligado)" 10 50
''',1)
# Execution: read fourth field and use item flag, fallback global only for old queue lines.
s=s.replace('''        pass=$(echo "$linha_fila" | cut -d'|' -f3)

        if [ -z "$pass" ]''','''        pass=$(echo "$linha_fila" | cut -d'|' -f3)
        tor_item=$(echo "$linha_fila" | cut -d'|' -f4)
        [ "$tor_item" != "1" ] && tor_item="${DOWNLOAD_TOR:-0}"

        if [ -z "$pass" ]''',1)
s=s.replace('''        [ "${DOWNLOAD_TOR:-0}" = 1 ] && echo "   Rede: Tor ($tor_proxy)"''','''        [ "$tor_item" = 1 ] && echo "   Rede: Tor ($tor_proxy)"''',1)
s=s.replace('''[ "${DOWNLOAD_TOR:-0}" = 1 ] && WGET_TOR_ARGS''','''[ "$tor_item" = 1 ] && WGET_TOR_ARGS''',1)
s=s.replace('''${DOWNLOAD_TOR:+$([ "${DOWNLOAD_TOR:-0}" = 1 ] && echo "--proxy=$tor_proxy")}''','''${tor_item:+$([ "$tor_item" = 1 ] && echo "--proxy=$tor_proxy")}''')
s=s.replace('''${DOWNLOAD_TOR:+$([ "${DOWNLOAD_TOR:-0}" = 1 ] && echo "--all-proxy=$tor_proxy")}''','''${tor_item:+$([ "$tor_item" = 1 ] && echo "--all-proxy=$tor_proxy")}''')
s=s.replace('''${DOWNLOAD_TOR:+$([ "${DOWNLOAD_TOR:-0}" = 1 ] && echo "--proxy=$tor_proxy")}''','''${tor_item:+$([ "$tor_item" = 1 ] && echo "--proxy=$tor_proxy")}''')
p.write_text(s)
