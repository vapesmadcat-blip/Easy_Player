from pathlib import Path
p=Path('/home/ubuntu/easy_player_current/eazy')
s=p.read_text()
s=s.replace('''        read -r -a YTDLP_EXTRA <<< "${DOWNLOAD_YTDLP_ARGS:-}"
        [ "${DOWNLOAD_TOR:-0}" = 1 ] && echo "   Rede: Tor ($tor_proxy)"''','''        read -r -a YTDLP_EXTRA <<< "${DOWNLOAD_YTDLP_ARGS:-}"
        WGET_TOR_ARGS=()
        [ "${DOWNLOAD_TOR:-0}" = 1 ] && WGET_TOR_ARGS=(-e use_proxy=on -e "all_proxy=$tor_proxy")
        [ "${DOWNLOAD_TOR:-0}" = 1 ] && echo "   Rede: Tor ($tor_proxy)"''')
s=s.replace('''wget "${WGET_EXTRA[@]}" ${DOWNLOAD_TOR:+$([ "${DOWNLOAD_TOR:-0}" = 1 ] && echo "-e use_proxy=on -e all_proxy=$tor_proxy")} -O''','''wget "${WGET_EXTRA[@]}" "${WGET_TOR_ARGS[@]}" -O''')
p.write_text(s)
