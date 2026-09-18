#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
VERSION="3.6.1"
python3 - "$ROOT" "$VERSION" <<'PY'
from pathlib import Path
import sys
root=Path(sys.argv[1]); version=sys.argv[2]
p=root/'eazy'
s=p.read_text().replace('EAZY_VERSION="3.6.0"', f'EAZY_VERSION="{version}"', 1)
old='''eazy_instalar_deb() {
    local pacote="$1" nome
    [ -f "$pacote" ] || return 1
'''
new='''eazy_instalar_deb() {
    local pacote="$1" nome
    [ -f "$pacote" ] || return 1
    clear 2>/dev/null || printf '\\033[2J\\033[H'
    printf '\\n=== Instalação de pacote Debian ===\\n\\n'
'''
if old not in s: raise SystemExit('função eazy_instalar_deb não encontrada')
s=s.replace(old,new,1)
s=s.replace('''    if ! command -v dpkg-deb >/dev/null 2>&1; then
        whiptail --title "Instalar pacote" --msgbox "dpkg-deb não está instalado." 8 60
        return 1
    fi''','''    if ! command -v dpkg-deb >/dev/null 2>&1; then
        whiptail --title "Instalar pacote" --msgbox "dpkg-deb não está instalado." 8 60
        read -r -p "Pressione Enter para voltar ao eazy..."
        return 1
    fi''',1)
s=s.replace('''        whiptail --title "Pacote inválido" --msgbox "Não foi possível ler:\\n$nome" 8 70
        return 1''','''        whiptail --title "Pacote inválido" --msgbox "Não foi possível ler:\\n$nome" 8 70
        read -r -p "Pressione Enter para voltar ao eazy..."
        return 1''',1)
s=s.replace('''    if ! whiptail --title "Instalar pacote Debian" --yesno "$info\\n\\nInstalar este pacote agora?" 16 78; then
        return 0
    fi''','''    if ! whiptail --title "Instalar pacote Debian" --yesno "$info\\n\\nInstalar este pacote agora?" 16 78; then
        read -r -p "Pressione Enter para voltar ao eazy..."
        return 0
    fi''',1)
s=s.replace('''        whiptail --title "Instalação" --msgbox "apt-get não encontrado.\\nUse: sudo dpkg -i '$pacote'" 9 70
        return 1''','''        whiptail --title "Instalação" --msgbox "apt-get não encontrado.\\nUse: sudo dpkg -i '$pacote'" 9 70
        read -r -p "Pressione Enter para voltar ao eazy..."
        return 1''',1)
s=s.replace('''        whiptail --title "Instalação concluída" --msgbox "Pacote instalado:\\n$nome" 8 65
        hash -r 2>/dev/null || true
    else
        whiptail --title "Falha na instalação" --msgbox "A instalação falhou.\\nTente:\\n sudo apt-get -f install" 10 70
        return 1
    fi''','''        whiptail --title "Instalação concluída" --msgbox "Pacote instalado:\\n$nome" 8 65
        hash -r 2>/dev/null || true
        read -r -p "Instalação concluída. Pressione Enter para voltar ao eazy..."
    else
        whiptail --title "Falha na instalação" --msgbox "A instalação falhou.\\nTente:\\n sudo apt-get -f install" 10 70
        read -r -p "Pressione Enter para voltar ao eazy..."
        return 1
    fi''',1)
p.write_text(s)
for name in ['eazy.1','packaging/eazy/debian/control']:
    p=root/name; p.write_text(p.read_text().replace('3.6.0',version))
p=root/'packaging/eazy/debian/changelog'; p.write_text(f'''eazy ({version}) unstable; urgency=medium\n\n  * Clear the terminal before local .deb installation.\n  * Pause after installation so the result remains visible before returning.\n\n -- eazy contributors <vapesmadcat-blip@users.noreply.github.com>  Fri, 18 Sep 2026 23:01:00 +0000\n\n'''+p.read_text())
p=root/'CHANGELOG.md'; p.write_text(p.read_text().replace('# Changelog\n', f'# Changelog\n\n## {version} — instalação .deb com tela limpa\n- Limpa a tela no início da instalação de um `.deb`.\n- Pausa no final para o resultado ficar visível antes de voltar ao eazy.\n'))
p=root/'README.md'; p.write_text(p.read_text().replace('# eazy 3.6.0 (release)', f'# eazy {version} (release)'))
p=root/'GUIA_RAPIDO.md'; p.write_text(p.read_text().replace('# Guia rápido do eazy 3.6.0', f'# Guia rápido do eazy {version}'))
p=root/'EAZY_EXPLICADO.md'; p.write_text(p.read_text().replace('# eazy 3.6.0', f'# eazy {version}',1))
p=root/'install-eazy-completo.sh'; p.write_text(p.read_text().replace('VERSION="3.6.0"', f'VERSION="{version}"'))
PY
