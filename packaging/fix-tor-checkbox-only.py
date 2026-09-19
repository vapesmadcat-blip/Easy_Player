from pathlib import Path
root=Path('/home/ubuntu/easy_player_current')
p=root/'eazy'; s=p.read_text().replace('EAZY_VERSION="3.8.2"','EAZY_VERSION="3.8.3"',1)
old='''        tor_item=$(echo "$linha_fila" | cut -d'|' -f4)
        [ "$tor_item" != "1" ] && tor_item="${DOWNLOAD_TOR:-0}"
'''
new='''        tor_item=$(echo "$linha_fila" | cut -d'|' -f4)
        # O checkbox do item tem prioridade: 0 desligado nunca herda Tor global.
        # Só filas antigas, sem quarto campo, usam o fallback global.
        if [ -z "$tor_item" ]; then
            tor_item="${DOWNLOAD_TOR:-0}"
        fi
        [ "$tor_item" = "1" ] || tor_item="0"
'''
if old not in s: raise SystemExit('bloco tor_item não encontrado')
s=s.replace(old,new,1)
for name in ['eazy.1','packaging/eazy/debian/control','install-eazy-completo.sh']:
 p=root/name; p.write_text(p.read_text().replace('3.8.2','3.8.3'))
p=root/'CHANGELOG.md'; p.write_text(p.read_text().replace('# Changelog\n','# Changelog\n\n## 3.8.3 — checkbox Tor com prioridade\n- Tor só é usado quando o checkbox do item está ligado.\n- O estado global não sobrescreve um checkbox desligado.\n'))
p=root/'packaging/eazy/debian/changelog'; p.write_text('''eazy (3.8.3) unstable; urgency=medium\n\n  * Respect the per-download Tor checkbox over the global fallback.\n\n -- eazy contributors <vapesmadcat-blip@users.noreply.github.com>  Fri, 19 Sep 2026 00:54:00 +0000\n\n'''+p.read_text())
for name in ['README.md','GUIA_RAPIDO.md','EAZY_EXPLICADO.md']:
 p=root/name; p.write_text(p.read_text().replace('3.8.2','3.8.3'))
