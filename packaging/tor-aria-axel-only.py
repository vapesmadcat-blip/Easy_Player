from pathlib import Path
root=Path('/home/ubuntu/easy_player_current'); version='3.8.1'
p=root/'eazy'; s=p.read_text().replace('EAZY_VERSION="3.8.0"',f'EAZY_VERSION="{version}"',1)
# Add torsocks command arrays and apply only to aria/axel when the queue item has Tor enabled.
s=s.replace('''        WGET_TOR_ARGS=()
        [ "$tor_item" = 1 ] && WGET_TOR_ARGS=(-e use_proxy=on -e "all_proxy=$tor_proxy")
        [ "$tor_item" = 1 ] && echo "   Rede: Tor ($tor_proxy)"''','''        TOR_PREFIX=()
        if [ "$tor_item" = 1 ]; then
            if command -v torsocks >/dev/null 2>&1; then
                TOR_PREFIX=(torsocks)
                echo "   Rede: Tor via torsocks (127.0.0.1:9050)"
            else
                echo "   Tor marcado, mas torsocks não está instalado."
            fi
        fi''',1)
s=s.replace('''aria2c "${ARIA_EXTRA[@]}" ${tor_item:+$([ "$tor_item" = 1 ] && echo "--all-proxy=$tor_proxy")} --allow-overwrite=true''','''"${TOR_PREFIX[@]}" aria2c "${ARIA_EXTRA[@]}" --allow-overwrite=true''',1)
s=s.replace('''axel "${AXEL_EXTRA[@]}" ${tor_item:+$([ "$tor_item" = 1 ] && echo "--proxy=$tor_proxy")} -o''','''"${TOR_PREFIX[@]}" axel "${AXEL_EXTRA[@]}" -o''',1)
# Keep wget available as a selectable legacy downloader, but do not present it as Tor method.
p.write_text(s)
# Replace docs additions with aria/Axel wording.
for name in ['README.md','GUIA_RAPIDO.md','EAZY_EXPLICADO.md']:
 q=root/name; x=q.read_text().replace('3.8.0',version)
 x=x.replace('Alternativas são `torsocks wget ...`, `wget -e use_proxy=yes -e socks_proxy=127.0.0.1:9050 ...` e `curl --socks5-hostname 127.0.0.1:9050 -O URL`.','Para aria2c/Axel, o eazy usa `torsocks` automaticamente quando o checkbox está marcado. Teste separadamente com `torsocks curl https://icanhazip.com`.')
 q.write_text(x)
p=root/'eazy.1'; x=p.read_text().replace('3.8.0',version)
x=x.replace('''Alternativas manuais:
.nf
torsocks wget http://exemplo.com
wget -e use_proxy=yes -e socks_proxy=127.0.0.1:9050 http://exemplo.com
curl --socks5-hostname 127.0.0.1:9050 -O http://exemplo.com
torsocks curl https://icanhazip.com
.fi''','''Para aria2c e Axel, o eazy prefixa o comando com torsocks quando o
checkbox Tor está marcado:
.nf
torsocks aria2c URL
torsocks axel --insecure -n 4 URL
torsocks curl https://icanhazip.com
.fi''')
p.write_text(x)
p=root/'CHANGELOG.md'; p.write_text(p.read_text().replace('# Changelog\n',f'# Changelog\n\n## {version} — Tor para aria2c e Axel\n- O checkbox Tor agora usa `torsocks` especificamente com aria2c e Axel.\n- A documentação deixa wget fora do fluxo principal de Tor.\n'))
p=root/'packaging/eazy/debian/control'; p.write_text(p.read_text().replace('3.8.0',version))
p=root/'packaging/eazy/debian/changelog'; p.write_text(f'''eazy ({version}) unstable; urgency=medium\n\n  * Use torsocks specifically for aria2c and Axel when Tor is selected.\n  * Update Tor documentation to focus on aria2c and Axel.\n\n -- eazy contributors <vapesmadcat-blip@users.noreply.github.com>  Fri, 19 Sep 2026 00:47:00 +0000\n\n'''+p.read_text())
p=root/'install-eazy-completo.sh'; p.write_text(p.read_text().replace('VERSION="3.8.0"',f'VERSION="{version}"'))
