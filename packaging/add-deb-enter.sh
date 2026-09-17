#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
VERSION="3.4.0"
python3 - "$ROOT" "$VERSION" <<'PY'
from pathlib import Path
import sys
root=Path(sys.argv[1]); version=sys.argv[2]
p=root/'eazy'
s=p.read_text().replace('EAZY_VERSION="3.3.9"', f'EAZY_VERSION="{version}"', 1)
needle='''eazy_abrir_arquivo_enter() {
    local tocado="$1"
    [ -z "$tocado" ] && return 1
'''
replacement='''eazy_instalar_deb() {
    local pacote="$1" nome
    [ -f "$pacote" ] || return 1
    nome=$(basename -- "$pacote")
    if ! command -v dpkg-deb >/dev/null 2>&1; then
        whiptail --title "Instalar pacote" --msgbox "dpkg-deb não está instalado." 8 60
        return 1
    fi
    local info
    info=$(dpkg-deb -f "$pacote" Package Version Description 2>/dev/null | sed -n '1,6p') || {
        whiptail --title "Pacote inválido" --msgbox "Não foi possível ler:\\n$nome" 8 70
        return 1
    }
    if ! whiptail --title "Instalar pacote Debian" --yesno "$info\\n\\nInstalar este pacote agora?" 16 78; then
        return 0
    fi
    if ! command -v apt-get >/dev/null 2>&1; then
        whiptail --title "Instalação" --msgbox "apt-get não encontrado.\\nUse: sudo dpkg -i '$pacote'" 9 70
        return 1
    fi
    if sudo apt-get install -y -- "$pacote"; then
        whiptail --title "Instalação concluída" --msgbox "Pacote instalado:\\n$nome" 8 65
        hash -r 2>/dev/null || true
    else
        whiptail --title "Falha na instalação" --msgbox "A instalação falhou.\\nTente:\\n sudo apt-get -f install" 10 70
        return 1
    fi
}

eazy_abrir_arquivo_enter() {
    local tocado="$1"
    [ -z "$tocado" ] && return 1
'''
if needle not in s: raise SystemExit('função Enter não encontrada')
s=s.replace(needle,replacement,1)
needle2='''    if [[ "$tocado" =~ ^https?:// ]]; then
        abrir_html_ou_link "$tocado"
        return $?
    fi
'''
replacement2=needle2+'''    if [[ "$tocado" =~ \\.deb$|\\.DEB$ ]]; then
        eazy_instalar_deb "$tocado"
        return $?
    fi
'''
s=s.replace(needle2,replacement2,1)
p.write_text(s)
for name in ['eazy.1','packaging/eazy/debian/control']:
    p=root/name; p.write_text(p.read_text().replace('3.3.9',version))
p=root/'packaging/eazy/debian/changelog'; p.write_text(f'''eazy ({version}) unstable; urgency=medium\n\n  * Install local Debian packages by pressing Enter on a .deb file.\n  * Show package metadata and request confirmation before apt installation.\n\n -- eazy contributors <vapesmadcat-blip@users.noreply.github.com>  Thu, 17 Sep 2026 19:58:00 +0000\n\n'''+p.read_text())
p=root/'CHANGELOG.md'; p.write_text(p.read_text().replace('# Changelog\n', f'# Changelog\n\n## {version} — instalar .deb com Enter\n- Pressionar Enter em um arquivo `.deb` abre o instalador integrado.\n- O pacote é conferido, mostra metadados e pede confirmação antes de usar o APT.\n'))
p=root/'README.md'; p.write_text(p.read_text().replace('# eazy 3.3.9 (release)', f'# eazy {version} (release)'))
p=root/'install-eazy-completo.sh'; p.write_text(p.read_text().replace('VERSION="3.3.9"', f'VERSION="{version}"'))
PY
