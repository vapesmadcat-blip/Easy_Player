from pathlib import Path
p=Path('/home/ubuntu/easy_player_current/eazy'); s=p.read_text()
needle='''elif [ "$1" = "--update-ytdlp" ]; then
'''
# Insert a branch immediately before update-ytdlp; it is safe and noninteractive.
branch='''elif [ "$1" = "--torrent" ]; then
    shift
    torrent_cmd="${EAZY_INSTALL_DIR}/torrent"
    [ -x "$torrent_cmd" ] || torrent_cmd="$(command -v torrent 2>/dev/null || true)"
    [ -n "$torrent_cmd" ] || { echo "CLI torrent não encontrado. Reinstale eazy." >&2; exit 1; }
    exec "$torrent_cmd" "$@"
'''
if branch not in s:
    if needle not in s: raise SystemExit('dispatcher marker not found')
    s=s.replace(needle,branch+needle,1)
# Ensure torrent engine case exists exactly before ytdlp.
if '            torrent)\n                torrent_cmd=' not in s:
    marker='''        case "$engine" in
            ytdlp)'''
    repl='''        case "$engine" in
            torrent)
                torrent_cmd="$EAZY_INSTALL_DIR/torrent"
                [ -x "$torrent_cmd" ] || torrent_cmd="$(command -v torrent 2>/dev/null || true)"
                if [ -z "$torrent_cmd" ]; then
                    echo -e "\\033[1;31mCLI torrent não encontrado. Reinstale eazy.\\033[0m"
                    status_dl=1
                else
                    torrent_args=(--dir "$download_dir")
                    [ "$tor_item" = 1 ] && torrent_args+=(--tor)
                    "$torrent_cmd" "${torrent_args[@]}" "$link_alvo" && status_dl=0
                fi
                ;;
            ytdlp)'''
    if marker not in s: raise SystemExit('engine marker not found')
    s=s.replace(marker,repl,1)
p.write_text(s)
