from pathlib import Path
root=Path('/home/ubuntu/easy_player_current'); version='3.9.2'
# Rename source command and update its presentation.
old=root/'torrent'; new=root/'eazy-tor'; data=old.read_text().replace('torrent - baixador CLI', 'eazy-tor - baixador CLI').replace('${CYAN}torrent${NC}', '${CYAN}eazy-tor${NC}')
new.write_text(data); old.unlink()
# Main eazy: queue manager invokes external eazy-tor; --torrent is compatibility forwarding only.
p=root/'eazy'; s=p.read_text().replace('EAZY_VERSION="3.9.1"',f'EAZY_VERSION="{version}"',1)
s=s.replace('''torrent_cmd="${EAZY_INSTALL_DIR}/torrent"
    [ -x "$torrent_cmd" ] || torrent_cmd="$(command -v torrent 2>/dev/null || true)"
    [ -n "$torrent_cmd" ] || { echo "CLI torrent não encontrado. Reinstale eazy." >&2; exit 1; }
    exec "$torrent_cmd" "$@"''','''torrent_cmd="${EAZY_INSTALL_DIR}/eazy-tor"
    [ -x "$torrent_cmd" ] || torrent_cmd="$(command -v eazy-tor 2>/dev/null || true)"
    [ -n "$torrent_cmd" ] || { echo "eazy-tor não encontrado. Instale o pacote eazy." >&2; exit 1; }
    exec "$torrent_cmd" "$@"''')
s=s.replace('''torrent_cmd="$EAZY_INSTALL_DIR/torrent"
                [ -x "$torrent_cmd" ] || torrent_cmd="$(command -v torrent 2>/dev/null || true)"''','''torrent_cmd="$EAZY_INSTALL_DIR/eazy-tor"
                [ -x "$torrent_cmd" ] || torrent_cmd="$(command -v eazy-tor 2>/dev/null || true)"''')
s=s.replace('CLI torrent não encontrado. Reinstale eazy.', 'eazy-tor não encontrado. Instale o pacote eazy.')
s=s.replace('''  --torrent [OPÇÕES] Executa o CLI torrent integrado (magnet/.torrent)''','''  --torrent [OPÇÕES] Encaminha para o downloader separado eazy-tor''')
p.write_text(s)
# Package eazy-tor instead of torrent.
p=root/'packaging/eazy/build-deb.sh'; s=p.read_text().replace('"$SRC_DIR/torrent"','"$SRC_DIR/eazy-tor"').replace('install -m 0755 "$SRC_DIR/torrent" "$PKGROOT/usr/bin/torrent"','install -m 0755 "$SRC_DIR/eazy-tor" "$PKGROOT/usr/bin/eazy-tor"'); p.write_text(s)
# Version/docs.
for name in ['eazy.1','README.md','GUIA_RAPIDO.md','EAZY_EXPLICADO.md','install-eazy-completo.sh']:
 p=root/name; p.write_text(p.read_text().replace('3.9.1',version).replace('`torrent`','`eazy-tor`').replace('torrent CLI','eazy-tor downloader'))
p=root/'eazy.1'; s=p.read_text().replace('''O pacote inclui o comando
.B eazy-tor''','''O pacote inclui o downloader separado
.B eazy-tor'''); s=s.replace('''que também é integrado ao eazy. Use `eazy --torrent` para chamar a mesma interface''','''que é chamado pelo gerenciador eazy quando um item torrent é executado. O eazy não faz o download diretamente.'''); p.write_text(s)
for name in ['README.md','GUIA_RAPIDO.md','EAZY_EXPLICADO.md']:
 p=root/name; x=p.read_text(); x += f'''\n\nArquitetura: o **eazy gerencia links e filas**; o downloader torrent fica separado no comando **`eazy-tor`**. O eazy chama `eazy-tor` somente quando a fila contém um magnet ou arquivo `.torrent`.\n'''; p.write_text(x)
p=root/'CHANGELOG.md'; p.write_text(p.read_text().replace('# Changelog\n',f'# Changelog\n\n## {version} — eazy-tor separado\n- eazy passa a gerenciar somente links e filas.\n- O download de torrents fica no executável separado `eazy-tor`.\n'))
p=root/'packaging/eazy/debian/control'; p.write_text(p.read_text().replace('3.9.1',version))
p=root/'packaging/eazy/debian/changelog'; p.write_text(f'''eazy ({version}) unstable; urgency=medium\n\n  * Split torrent downloading into the separate eazy-tor executable.\n  * Keep eazy focused on link and queue management.\n\n -- eazy contributors <vapesmadcat-blip@users.noreply.github.com>  Fri, 19 Sep 2026 01:45:00 +0000\n\n'''+p.read_text())
