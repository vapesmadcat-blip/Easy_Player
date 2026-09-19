from pathlib import Path
root=Path('/home/ubuntu/easy_player_current'); version='3.9.0'
# Version and user docs
for name in ['eazy','eazy.1','README.md','GUIA_RAPIDO.md','EAZY_EXPLICADO.md','install-eazy-completo.sh']:
 p=root/name; p.write_text(p.read_text().replace('3.8.4',version))
p=root/'eazy.1'; s=p.read_text(); block='''\n.SH TORRENT CLI\nO pacote inclui o comando\n.B torrent\npara downloads BitTorrent via aria2c. Ele aceita arquivos .torrent e links magnet.\n.nf\ntorrent arquivo.torrent\ntorrent --tor "magnet:?xt=urn:btih:..."\ntorrent -d /mnt/torrents --no-seed arquivo.torrent\n.fi\nO destino padrão é\n.B ~/Downloads/Torrents .\nUse\n.B --tor\npara prefixar aria2c com torsocks; isso só é ativado quando a opção é informada.\n'''
if '.SH TORRENT CLI' not in s: s=s.replace('.SH TOR SETUP',block+'\n.SH TOR SETUP',1)
p.write_text(s)
for name in ['README.md','GUIA_RAPIDO.md','EAZY_EXPLICADO.md']:
 p=root/name; x=p.read_text(); x += f'''\n\n## CLI torrent\n\nA versão {version} inclui o comando `torrent`, baseado em aria2c, para arquivos `.torrent` e links magnet. O destino padrão é `~/Downloads/Torrents`. Exemplos: `torrent arquivo.torrent`, `torrent --tor "magnet:?xt=urn:btih:..."` e `torrent -d /mnt/torrents --no-seed arquivo.torrent`. A opção `--tor` usa `torsocks` somente quando informada.\n'''; p.write_text(x)
p=root/'CHANGELOG.md'; p.write_text(p.read_text().replace('# Changelog\n',f'# Changelog\n\n## {version} — CLI torrent\n- Incluído o comando `torrent` para arquivos `.torrent` e links magnet.\n- Suporte a destino, ratio, peers, `--no-seed`, `--show` e `--tor`.\n'))
p=root/'packaging/eazy/debian/control'; p.write_text(p.read_text().replace('3.8.4',version).replace('aria2, axel','aria2, torsocks, axel'))
p=root/'packaging/eazy/debian/changelog'; p.write_text(f'''eazy ({version}) unstable; urgency=medium\n\n  * Add torrent CLI wrapper around aria2c with magnet, seed and optional Tor support.\n\n -- eazy contributors <vapesmadcat-blip@users.noreply.github.com>  Fri, 19 Sep 2026 01:40:00 +0000\n\n'''+p.read_text())
# Package torrent binary
p=root/'packaging/eazy/build-deb.sh'; s=p.read_text()
s=s.replace('''"$SRC_DIR/eazy" "$SRC_DIR/eazy-ai.py"''','''"$SRC_DIR/eazy" "$SRC_DIR/torrent" "$SRC_DIR/eazy-ai.py"''',1)
s=s.replace('''install -m 0755 "$SRC_DIR/eazy" "$PKGROOT/usr/bin/eazy"''','''install -m 0755 "$SRC_DIR/eazy" "$PKGROOT/usr/bin/eazy"\ninstall -m 0755 "$SRC_DIR/torrent" "$PKGROOT/usr/bin/torrent"''',1)
p.write_text(s)
