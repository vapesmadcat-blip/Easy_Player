#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
VERSION="3.5.0"
python3 - "$ROOT" "$VERSION" <<'PY'
from pathlib import Path
import sys
root=Path(sys.argv[1]); version=sys.argv[2]

p=root/'eazy'; s=p.read_text().replace('EAZY_VERSION="3.4.0"', f'EAZY_VERSION="{version}"', 1)
s=s.replace('''  Enter              Tocar só o item sob o cursor / entrar na pasta
''','''  Enter              Abrir/tocar; em .deb mostra dados e instala com confirmação
''',1)
s=s.replace('''  F10                Ajuda expandida
''','''  F10                Ajuda expandida (atalhos, instalação .deb e configuração)
''',1)
s=s.replace('''Dependências: fzf, mpv (ou mplayer/cvlc/ffplay), whiptail, find, awk
Opcionais: yt-dlp, aria2c, axel, chafa, ffmpeg, p7zip-full, smartmontools
''','''Em um arquivo .deb: pressione Enter para conferir o pacote e instalar com APT.
A lista usa TAM · DATA · TIPO e mantém o ciclo visual idx3 de três cores.

Dependências: fzf, mpv (ou mplayer/cvlc/ffplay), whiptail, find, awk
Opcionais: yt-dlp, aria2c, axel, chafa, ffmpeg, p7zip-full, smartmontools
''',1)
p.write_text(s)

p=root/'eazy.1'; s=p.read_text()
s=s.replace('eazy 3.4.0', f'eazy {version}')
s=s.replace('eazy_3.2.3_all.deb', f'eazy_{version}_all.deb').replace('eazy-v3.2.3', f'eazy-v{version}')
s=s.replace('''\.B Enter
Tocar / abrir só o item sob o cursor; entrar em pasta; abrir playlist
.BR .m3u .
''','''\.B Enter
Tocar / abrir só o item sob o cursor; entrar em pasta; abrir playlist
.BR .m3u .
Em arquivos
.BR .deb ,
mostra os metadados e oferece instalação confirmada pelo APT.
''',1)
s=s.replace('''\.SH BUGS
''','''\.SH DISPLAY FORMAT
A lista principal e os resultados de busca exibem as informações no formato
.B TAM · DATA · TIPO .
O tamanho é mostrado primeiro para facilitar a comparação. As cores de linha
seguem o ciclo visual de três cores
.BR idx3 ;
a cor não representa uma diferença de codec ou qualidade do vídeo.
.SH DEBIAN PACKAGE INSTALLATION
Ao posicionar o cursor sobre um arquivo
.BR .deb
 e pressionar
.BR Enter ,
o eazy lê o nome, a versão e a descrição, pede confirmação e executa:
.nf
sudo apt-get install -y ./pacote.deb
.fi
A instalação não é executada sem confirmação. Se o pacote tiver dependências
pendentes, use
.BR "sudo apt-get -f install" .
.SH BUGS
''',1)
p.write_text(s)

p=root/'README.md'; s=p.read_text()
s=s.replace('# eazy 3.3.9 (release)', f'# eazy {version} (release)').replace('# eazy 3.4.0 (release)', f'# eazy {version} (release)')
s=s.replace('eazy_3.3.9_all.deb',f'eazy_{version}_all.deb').replace('eazy_3.4.0_all.deb',f'eazy_{version}_all.deb')
s += f'''\n## Atualização {version}\n\n- **Enter em `.deb`**: exibe os metadados, pede confirmação e instala pelo APT.\n- **Lista**: mostra `TAM · DATA · TIPO`; as cores seguem o ciclo visual `idx3`.\n- **Ajuda**: `eazy --help` e `F10` incluem os atalhos e o fluxo de instalação.\n- **Manual**: `man eazy` documenta todos esses recursos.\n'''
p.write_text(s)

p=root/'GUIA_RAPIDO.md'; s=p.read_text()
s=s.replace('# Guia rápido do eazy', f'# Guia rápido do eazy {version}')
s += f'''\n## Instalar pacotes `.deb` com Enter\n\nNavegue até um arquivo `.deb` e pressione **Enter**. O eazy mostra nome, versão e descrição, pede confirmação e chama o APT para instalar o pacote. A instalação requer confirmação explícita.\n\n## Formato e cores da lista\n\nA informação aparece como **TAM · DATA · TIPO**. As cores seguem o ciclo visual **idx3** de três cores por posição da linha; isso é apenas uma marca visual e não indica diferença entre vídeos.\n\n## Ajuda e manual\n\nUse `eazy --help` para a ajuda no terminal, `F10` para a ajuda interativa e `man eazy` para a referência completa.\n'''
p.write_text(s)

p=root/'EAZY_EXPLICADO.md'; s=p.read_text()
s=s.replace('# eazy — documentação completa de funcionamento e vantagens', f'# eazy {version} — documentação completa de funcionamento e vantagens')
s += f'''\n\n## Atualização {version}: pacotes, formato e ajuda\n\nAo selecionar um arquivo `.deb` e pressionar **Enter**, o eazy lê os metadados do pacote, solicita confirmação e executa a instalação local com APT. O fluxo é intencionalmente confirmado para evitar instalações acidentais.\n\nA listagem mostra o tamanho antes da data e do tipo: **TAM · DATA · TIPO**. O ciclo de três cores `idx3` é uma convenção visual baseada na posição da linha; ele não representa qualidade, codec ou estado do vídeo.\n\nA documentação operacional está disponível em três níveis: `eazy --help` para comandos e atalhos no terminal, `F10` para a ajuda interativa durante a navegação e `man eazy` para a referência detalhada.\n'''
p.write_text(s)

p=root/'install-eazy-completo.sh'; s=p.read_text().replace('VERSION="3.4.0"', f'VERSION="{version}"'); p.write_text(s)

p=root/'CHANGELOG.md'; s=p.read_text().replace('# Changelog\n', f'# Changelog\n\n## {version} — atualização completa da documentação\n- Atualizados `eazy --help`, F10, `man eazy`, README, guia rápido e documentação completa.\n- Documentado o Enter em `.deb`, instalação confirmada pelo APT, formato TAM · DATA · TIPO e ciclo idx3.\n- Removidas referências antigas de versão nos exemplos principais.\n'); p.write_text(s)

p=root/'packaging/eazy/debian/control'; s=p.read_text().replace('Version: 3.4.0', f'Version: {version}'); p.write_text(s)
p=root/'packaging/eazy/debian/changelog'; p.write_text(f'''eazy ({version}) unstable; urgency=medium\n\n  * Update CLI help, F10 help, man page and all user documentation.\n  * Document Enter-to-install for local .deb packages, TAM/DATA/TIPO and idx3 colors.\n\n -- eazy contributors <vapesmadcat-blip@users.noreply.github.com>  Thu, 17 Sep 2026 20:02:00 +0000\n\n'''+p.read_text())
PY
