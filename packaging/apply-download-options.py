from pathlib import Path
root=Path('/home/ubuntu/easy_player_current')
p=root/'eazy'; s=p.read_text()
s=s.replace('EAZY_VERSION="3.6.1"','EAZY_VERSION="3.7.0"',1)
s=s.replace('''DOWNLOAD_DIR="${HOME}/Downloads"  # padrão: ~/Downloads
PLAYER_PADRAO''','''DOWNLOAD_DIR="${HOME}/Downloads"  # padrão: ~/Downloads
DOWNLOAD_ENGINE="aria"          # downloader automático para links diretos
DOWNLOAD_TOR="0"                # 0=desligado | 1=SOCKS5 127.0.0.1:9050
DOWNLOAD_ARIA_ARGS="--console-log-level=notice -x 4 -s 4 --auto-file-renaming=false"
DOWNLOAD_AXEL_ARGS="--insecure -n 4"
DOWNLOAD_WGET_ARGS="--no-check-certificate"
DOWNLOAD_YTDLP_ARGS=""
PLAYER_PADRAO''',1)
s=s.replace('''DOWNLOAD_DIR="${DOWNLOAD_DIR:-${HOME}/Downloads}"
SEL_GLOBAL_OP''','''DOWNLOAD_DIR="${DOWNLOAD_DIR:-${HOME}/Downloads}"
DOWNLOAD_ENGINE="${DOWNLOAD_ENGINE:-aria}"
DOWNLOAD_TOR="${DOWNLOAD_TOR:-0}"
DOWNLOAD_ARIA_ARGS="${DOWNLOAD_ARIA_ARGS:---console-log-level=notice -x 4 -s 4 --auto-file-renaming=false}"
DOWNLOAD_AXEL_ARGS="${DOWNLOAD_AXEL_ARGS:---insecure -n 4}"
DOWNLOAD_WGET_ARGS="${DOWNLOAD_WGET_ARGS:---no-check-certificate}"
DOWNLOAD_YTDLP_ARGS="${DOWNLOAD_YTDLP_ARGS:-}"
SEL_GLOBAL_OP''',1)
# add config function before configurar_defaults
if 'configurar_downloads() {' not in s:
    marker='configurar_defaults() {'
    fn='''configurar_downloads() {\n    local motor tor aria axel wget ytdlp\n    motor=$(whiptail --title "Downloader padrão" --radiolist "Links diretos (vídeos continuam no yt-dlp):" 14 72 4 "aria" "aria2c (padrão)" $( [ "${DOWNLOAD_ENGINE:-aria}" = aria ] && echo ON || echo OFF ) "axel" "Axel" $( [ "${DOWNLOAD_ENGINE:-aria}" = axel ] && echo ON || echo OFF ) "wget" "Wget" $( [ "${DOWNLOAD_ENGINE:-aria}" = wget ] && echo ON || echo OFF ) "ytdlp" "yt-dlp" $( [ "${DOWNLOAD_ENGINE:-aria}" = ytdlp ] && echo ON || echo OFF ) 3>&1 1>&2 2>&3) || return\n    [ -n "$motor" ] && DOWNLOAD_ENGINE="$motor"\n    tor=$(whiptail --title "Rede Tor" --radiolist "Tor deve estar ativo em 127.0.0.1:9050:" 10 70 2 "0" "Desligado (padrão)" $( [ "${DOWNLOAD_TOR:-0}" = 0 ] && echo ON || echo OFF ) "1" "Usar Tor SOCKS5" $( [ "${DOWNLOAD_TOR:-0}" = 1 ] && echo ON || echo OFF ) 3>&1 1>&2 2>&3) || return\n    DOWNLOAD_TOR="${tor:-0}"\n    aria=$(whiptail --title "Parâmetros aria2c" --inputbox "Parâmetros extras:" 9 75 "${DOWNLOAD_ARIA_ARGS:-}" 3>&1 1>&2 2>&3) || return\n    axel=$(whiptail --title "Parâmetros Axel" --inputbox "Default: --insecure -n 4" 9 75 "${DOWNLOAD_AXEL_ARGS:---insecure -n 4}" 3>&1 1>&2 2>&3) || return\n    wget=$(whiptail --title "Parâmetros Wget" --inputbox "Parâmetros extras:" 9 75 "${DOWNLOAD_WGET_ARGS:---no-check-certificate}" 3>&1 1>&2 2>&3) || return\n    ytdlp=$(whiptail --title "Parâmetros yt-dlp" --inputbox "Parâmetros extras:" 9 75 "${DOWNLOAD_YTDLP_ARGS:-}" 3>&1 1>&2 2>&3) || return\n    DOWNLOAD_ARIA_ARGS="$aria"; DOWNLOAD_AXEL_ARGS="$axel"; DOWNLOAD_WGET_ARGS="$wget"; DOWNLOAD_YTDLP_ARGS="$ytdlp"\n    cat >> "$CONFIG_FILE" <<EOF\nDOWNLOAD_ENGINE="$DOWNLOAD_ENGINE"\nDOWNLOAD_TOR="$DOWNLOAD_TOR"\nDOWNLOAD_ARIA_ARGS="$DOWNLOAD_ARIA_ARGS"\nDOWNLOAD_AXEL_ARGS="$DOWNLOAD_AXEL_ARGS"\nDOWNLOAD_WGET_ARGS="$DOWNLOAD_WGET_ARGS"\nDOWNLOAD_YTDLP_ARGS="$DOWNLOAD_YTDLP_ARGS"\nEOF\n    whiptail --title "Downloads" --msgbox "Salvo.\nDownloader: $DOWNLOAD_ENGINE\nTor: $([ "$DOWNLOAD_TOR" = 1 ] && echo ATIVO || echo desligado)" 9 60\n}\n\n'''
    s=s.replace(marker,fn+marker,1)
s=s.replace('''        "config" "Configurar o eazy (inclui destino de downloads)"''','''        "config" "Configurar o eazy (inclui downloads/Tor)"''',1)
s=s.replace('''        "exitdir" "Ao sair: dir do navegador ou o anterior"''','''        "exitdir" "Ao sair: dir do navegador ou o anterior"\n        "download" "Downloads — downloader/Tor/parâmetros"''',1)
s=s.replace('''        exitdir) configurar_dir_saida; return ;;''','''        exitdir) configurar_dir_saida; return ;;\n        download) configurar_downloads; return ;;''',1)
# direct links: automatic, no radio menu
start='''        # Arquivo direto: aria / axel / wget / yt-dlp
        gerenciador=$(whiptail --title "Escolher Ferramenta"'''
if start in s:
    a=s.index(start); b=s.index('''        if [ "$gerenciador" = "ytdlp" ]; then''',a)
    s=s[:a]+'''        # Link direto: usa o downloader configurado, sem perguntar a cada vez.
        gerenciador="${DOWNLOAD_ENGINE:-aria}"
        if [ "$gerenciador" = "ytdlp" ]; then
'''+s[b+len('''        if [ "$gerenciador" = "ytdlp" ]; then
'''):]
# execution setup
s=s.replace('''        download_dir="${DOWNLOAD_DIR:-${HOME}/Downloads}"
        mkdir -p''','''        download_dir="${DOWNLOAD_DIR:-${HOME}/Downloads}"
        tor_proxy="socks5://127.0.0.1:9050"
        read -r -a ARIA_EXTRA <<< "${DOWNLOAD_ARIA_ARGS:-}"
        read -r -a AXEL_EXTRA <<< "${DOWNLOAD_AXEL_ARGS:---insecure -n 4}"
        read -r -a WGET_EXTRA <<< "${DOWNLOAD_WGET_ARGS:---no-check-certificate}"
        read -r -a YTDLP_EXTRA <<< "${DOWNLOAD_YTDLP_ARGS:-}"
        [ "${DOWNLOAD_TOR:-0}" = 1 ] && echo "   Rede: Tor ($tor_proxy)"
        mkdir -p''',1)
# use args in commands
s=s.replace('''aria2c --console-log-level=notice -x 4 -s 4 --auto-file-renaming=false \\
                        --allow-overwrite=true "$link_alvo"''','''aria2c "${ARIA_EXTRA[@]}" --allow-overwrite=true "$link_alvo"''',1)
s=s.replace('''axel --insecure -n 4 -o "$download_dir/$nome_esperado" "$link_alvo"''','''axel "${AXEL_EXTRA[@]}" -o "$download_dir/$nome_esperado" "$link_alvo"''',1)
s=s.replace('''wget --no-check-certificate -O "$download_dir/$nome_esperado" "$link_alvo"''','''wget "${WGET_EXTRA[@]}" -O "$download_dir/$nome_esperado" "$link_alvo"''',1)
# add proxy to non-ytdlp tools in a simple safe way
s=s.replace('''aria2c "${ARIA_EXTRA[@]}" --allow-overwrite=true "$link_alvo"''','''aria2c "${ARIA_EXTRA[@]}" ${DOWNLOAD_TOR:+$([ "${DOWNLOAD_TOR:-0}" = 1 ] && echo "--all-proxy=$tor_proxy")} --allow-overwrite=true "$link_alvo"''',1)
s=s.replace('''axel "${AXEL_EXTRA[@]}" -o''','''axel "${AXEL_EXTRA[@]}" ${DOWNLOAD_TOR:+$([ "${DOWNLOAD_TOR:-0}" = 1 ] && echo "--proxy=$tor_proxy")} -o''',1)
s=s.replace('''wget "${WGET_EXTRA[@]}" -O''','''wget "${WGET_EXTRA[@]}" ${DOWNLOAD_TOR:+$([ "${DOWNLOAD_TOR:-0}" = 1 ] && echo "-e use_proxy=on -e all_proxy=$tor_proxy")} -O''',1)
# docs and version
for name in ['eazy.1','packaging/eazy/debian/control']:
    q=root/name; q.write_text(q.read_text().replace('3.6.1','3.7.0'))
for name in ['README.md','GUIA_RAPIDO.md','EAZY_EXPLICADO.md','install-eazy-completo.sh']:
    q=root/name; q.write_text(q.read_text().replace('3.6.1','3.7.0'))
p.write_text(s)
