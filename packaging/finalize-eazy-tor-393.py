from pathlib import Path
root=Path('/home/ubuntu/easy_player_current')
p=root/'packaging/eazy/build-deb.sh'; p.write_text(p.read_text().replace('$PKGROOT/usr/bin/torrent','$PKGROOT/usr/bin/eazy-tor'))
p=root/'eazy-tor'; s=p.read_text().replace('Uso: torrent ', 'Uso: eazy-tor ').replace('  torrent arquivo', '  eazy-tor arquivo').replace('  torrent --tor', '  eazy-tor --tor').replace('  torrent -d', '  eazy-tor -d'); p.write_text(s)
for name in ['eazy','eazy.1','README.md','GUIA_RAPIDO.md','EAZY_EXPLICADO.md','install-eazy-completo.sh','packaging/eazy/debian/control']:
 p=root/name; p.write_text(p.read_text().replace('3.9.2','3.9.3'))
p=root/'CHANGELOG.md'; p.write_text(p.read_text().replace('# Changelog\n','# Changelog\n\n## 3.9.3 — eazy-tor como downloader separado\n- O pacote instala o downloader em `/usr/bin/eazy-tor`.\n'))
p=root/'packaging/eazy/debian/changelog'; p.write_text('''eazy (3.9.3) unstable; urgency=medium\n\n  * Install the separate torrent downloader as eazy-tor.\n\n -- eazy contributors <vapesmadcat-blip@users.noreply.github.com>  Fri, 19 Sep 2026 01:46:00 +0000\n\n'''+p.read_text())
