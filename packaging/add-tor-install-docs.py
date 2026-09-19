from pathlib import Path
root=Path('/home/ubuntu/easy_player_current'); version='3.8.0'
p=root/'eazy'; s=p.read_text().replace('EAZY_VERSION="3.7.0"',f'EAZY_VERSION="{version}"',1)
# Include Tor packages in the existing --install dependency lists.
s=s.replace('''instalar_pkgs apt fzf mpv mplayer gawk sed findutils whiptail wget curl file axel aria2 unzip''','''instalar_pkgs apt fzf mpv mplayer gawk sed findutils whiptail wget curl file axel aria2 tor torsocks unzip''',1)
s=s.replace('''instalar_pkgs pacman fzf mpv mplayer gawk sed findutils libnewt wget axel aria2 unzip''','''instalar_pkgs pacman fzf mpv mplayer gawk sed findutils libnewt wget axel aria2 tor torsocks unzip''',1)
s=s.replace('''instalar_pkgs dnf fzf mpv mplayer gawk sed findutils newt wget axel aria2 unzip''','''instalar_pkgs dnf fzf mpv mplayer gawk sed findutils newt wget axel aria2 tor torsocks unzip''',1)
s=s.replace('''instalar_pkgs zypper fzf mpv mplayer gawk sed findutils newt wget axel aria2 unzip''','''instalar_pkgs zypper fzf mpv mplayer gawk sed findutils newt wget axel aria2 tor torsocks unzip''',1)
s=s.replace('''instalar_pkgs apk fzf mpv mplayer gawk sed findutils newt wget axel aria2 unzip''','''instalar_pkgs apk fzf mpv mplayer gawk sed findutils newt wget axel aria2 tor torsocks unzip''',1)
s=s.replace('''  F10                Ajuda expandida (atalhos, instalação .deb e configuração)''','''  F10                Ajuda expandida (atalhos, .deb, downloads, Tor e configuração)''',1)
s=s.replace('''Downloads: escolha aria/axel/wget/yt-dlp; Tor SOCKS5 opcional em F9; parâmetros extras por motor.''','''Downloads: links diretos usam o downloader atual; o checkbox Tor usa SOCKS5 127.0.0.1:9050; parâmetros extras ficam em F9.''',1)
p.write_text(s)
# bump docs and add procedure
for name in ['eazy.1','README.md','GUIA_RAPIDO.md','EAZY_EXPLICADO.md','install-eazy-completo.sh']:
 q=root/name; x=q.read_text().replace('3.7.0',version); q.write_text(x)
p=root/'eazy.1'; x=p.read_text(); marker='.SH MAINTENANCE\n'; block='''.SH TOR SETUP\nA instalação pelo comando\n.B eazy --install\ntambém inclui\n.B tor\ne\n.B torsocks\nquando disponíveis no gerenciador da distribuição. Para instalar manualmente\nem Debian, Ubuntu ou Mint:\n.nf\nsudo apt update && sudo apt install tor torsocks -y\n.fi\nFedora/RHEL:\n.nf\nsudo dnf install tor torsocks -y\n.fi\nArch Linux:\n.nf\nsudo pacman -S tor torsocks\n.fi\nInicie o serviço e, opcionalmente, habilite-o no boot:\n.nf\nsudo systemctl start tor\nsudo systemctl enable tor\n.fi\nAo adicionar um link, marque\n.B Usar Tor neste download .\nO eazy usará SOCKS5 em\n.B 127.0.0.1:9050 .\nAlternativas manuais:\n.nf\ntorsocks wget http://exemplo.com\nwget -e use_proxy=yes -e socks_proxy=127.0.0.1:9050 http://exemplo.com\ncurl --socks5-hostname 127.0.0.1:9050 -O http://exemplo.com\ntorsocks curl https://icanhazip.com\n.fi\n''';
if '.SH TOR SETUP' not in x: x=x.replace(marker,block+marker,1)
p.write_text(x)
for name in ['README.md','GUIA_RAPIDO.md','EAZY_EXPLICADO.md']:
 q=root/name; x=q.read_text(); x += f'''\n\n## Tor e torsocks\n\nO instalador `eazy --install` inclui `tor` e `torsocks` quando o sistema oferece esses pacotes. Manualmente, use `sudo apt update && sudo apt install tor torsocks -y` (Debian/Ubuntu/Mint), `sudo dnf install tor torsocks -y` (Fedora/RHEL) ou `sudo pacman -S tor torsocks` (Arch). Inicie com `sudo systemctl start tor` e, se desejar, `sudo systemctl enable tor`.\n\nAo adicionar um link, marque **Usar Tor neste download**. O eazy usa SOCKS5 em `127.0.0.1:9050`. Para testar: `torsocks curl https://icanhazip.com`. Alternativas são `torsocks wget ...`, `wget -e use_proxy=yes -e socks_proxy=127.0.0.1:9050 ...` e `curl --socks5-hostname 127.0.0.1:9050 -O URL`.\n'''; q.write_text(x)
p=root/'CHANGELOG.md'; p.write_text(p.read_text().replace('# Changelog\n',f'# Changelog\n\n## {version} — instalação e documentação Tor\n- `eazy --install` inclui `tor` e `torsocks` nas distribuições suportadas.\n- Documentados instalação, inicialização, teste de IP e uso do checkbox Tor.\n'))
p=root/'packaging/eazy/debian/control'; p.write_text(p.read_text().replace('3.7.0',version))
p=root/'packaging/eazy/debian/changelog'; p.write_text(f'''eazy ({version}) unstable; urgency=medium\n\n  * Include tor and torsocks in the optional dependency installer.\n  * Document Tor setup, service startup, testing and per-download checkbox.\n\n -- eazy contributors <vapesmadcat-blip@users.noreply.github.com>  Fri, 19 Sep 2026 00:45:00 +0000\n\n'''+p.read_text())
