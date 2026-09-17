#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
VERSION="3.3.1"

python3 - "$ROOT" "$VERSION" <<'PY'
from pathlib import Path
import sys
root=Path(sys.argv[1]); version=sys.argv[2]

p=root/'eazy'
s=p.read_text()
s=s.replace('EAZY_VERSION="3.3"', f'EAZY_VERSION="{version}"', 1)
s=s.replace('    echo "${EAZY_NAME} ${EAZY_VERSION} (${EAZY_CODENAME})"', '    printf "\\033[1;32m%s %s (%s)\\033[0m\\n" "$EAZY_NAME" "$EAZY_VERSION" "$EAZY_CODENAME"', 1)
p.write_text(s)

p=root/'eazy.1'
s=p.read_text()
s=s.replace('.TH EAZY 1 "2026-09-16" "eazy 3.2.12" "User Commands"', '.TH EAZY 1 "2026-09-17" "eazy 3.3.1" "User Commands"')
s=s.replace('.BR "eazy 3.2.3 (release)"', '.BR "eazy 3.3.1 (IA)"')
s=s.replace('.SH MAINTENANCE', '''.SH DESKTOP INTEGRATION
O pacote base funciona em qualquer ambiente Linux com terminal. Os metapacotes
.B eazy-gnome
 e
.B eazy-kde
 adicionam as ferramentas recomendadas para GNOME e KDE Plasma,
respectivamente, sem duplicar o executável principal.
.P
O launcher
.I eazy.desktop
usa
.B Terminal=true
 e aparece nos menus GNOME, KDE Plasma e outros ambientes compatíveis com
freedesktop.org. O instalador detecta o ambiente ativo e tenta instalar as
dependências opcionais correspondentes.
.SH AI CONFIGURATION
A IA é opcional. Configure a chave sem gravá-la no código:
.nf
mkdir -p ~/.config/eazy
printf 'EAZY_AI_API_KEY=%s\\n' 'sua-chave' > ~/.config/eazy/ai.env
chmod 600 ~/.config/eazy/ai.env
eazy --ai
.fi
A chave também pode ser fornecida pela variável
.B EAZY_AI_API_KEY
. A configuração pessoal é preservada ao remover o pacote.
.SH MAINTENANCE''')
s=s.replace('curl -fsSL -o eazy_3.2.3_all.deb \\\n  https://github.com/vapesmadcat-blip/Easy_Player/releases/download/eazy-v3.2.3/eazy_3.2.3_all.deb\nsudo apt install ./eazy_3.2.3_all.deb', 'curl -fsSL -o eazy_3.3.1_all.deb \\\n  https://github.com/vapesmadcat-blip/Easy_Player/releases/download/eazy-v3.3.1/eazy_3.3.1_all.deb\nsudo apt install ./eazy_3.3.1_all.deb')
s=s.replace('.SH BUGS', '''.TP
Instalar integração GNOME:
.nf
sudo apt install ./eazy-gnome_3.3.1_all.deb
.fi
.TP
Instalar integração KDE Plasma:
.nf
sudo apt install ./eazy-kde_3.3.1_all.deb
.fi
.SH BUGS''')
p.write_text(s)

p=root/'README.md'
s=p.read_text().replace('# eazy 3.3 (release)', '# eazy 3.3.1 (release)')
s=s.replace('sudo dpkg -i eazy_3.3_all.deb && sudo apt-get install -f', 'sudo dpkg -i eazy_3.3.1_all.deb && sudo apt-get install -f\n# GNOME: sudo apt install ./eazy-gnome_3.3.1_all.deb\n# KDE Plasma: sudo apt install ./eazy-kde_3.3.1_all.deb')
s=s.replace('`eazy --version`', '`eazy --version` (a versão é exibida em verde)')
p.write_text(s)

p=root/'CHANGELOG.md'
s=p.read_text().replace('# Changelog\n', '# Changelog\n\n## 3.3.1 — GNOME/KDE\n- Saída de `eazy --version` exibida em verde.\n- Manual `eazy(1)` atualizado para 3.3.1, IA e integração de desktops.\n- Metapacote `eazy-gnome` com terminal, gerenciador de arquivos e utilitários GNOME.\n- Metapacote `eazy-kde` com Konsole, Dolphin, Kate e integração KDE.\n- Ambos os metapacotes dependem do `eazy` base e não duplicam seus arquivos.\n')
p.write_text(s)
PY

sed -i 's/^Version: .*/Version: 3.3.1/' "$ROOT/packaging/eazy/debian/control"
cat > "$ROOT/packaging/eazy/debian/changelog" <<'EOF'
eazy (3.3.1) unstable; urgency=medium

  * Update eazy(1) for 3.3.1, AI configuration and desktop integration.
  * Display --version output in green.
  * Add separate eazy-gnome and eazy-kde meta-packages.

 -- eazy contributors <vapesmadcat-blip@users.noreply.github.com>  Thu, 17 Sep 2026 18:27:00 +0000
EOF

mkdir -p "$ROOT/packaging/desktop/debian"
cat > "$ROOT/packaging/desktop/build-desktop-pkgs.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd -P)"
VERSION="${1:-3.3.1}"
DIST="$ROOT/packaging/desktop/dist"
rm -rf "$ROOT/packaging/desktop/pkgroot-gnome" "$ROOT/packaging/desktop/pkgroot-kde"
mkdir -p "$DIST"
make_meta() {
  local flavor="$1"; shift
  local root="$ROOT/packaging/desktop/pkgroot-$flavor"
  local pkg="eazy-$flavor"
  mkdir -p "$root/DEBIAN" "$root/usr/share/doc/$pkg"
  cat > "$root/DEBIAN/control" <<CONTROL
Package: $pkg
Version: $VERSION
Section: video
Priority: optional
Architecture: all
Maintainer: eazy contributors <vapesmadcat-blip@users.noreply.github.com>
Depends: eazy (= $VERSION)
Recommends: $*
Description: eazy desktop integration for ${flavor^}
 Meta-package for eazy with recommended ${flavor^} terminal, file manager and
 desktop utilities. The eazy executable is provided by the base eazy package.
CONTROL
  printf 'eazy desktop integration %s\n' "$VERSION" > "$root/usr/share/doc/$pkg/README"
  dpkg-deb --build --root-owner-group "$root" "$DIST/${pkg}_${VERSION}_all.deb" >/dev/null
}
make_meta gnome "gnome-terminal nautilus gedit evince xdg-utils"
make_meta kde "konsole dolphin kate kio-extras xdg-utils"
printf 'Pacotes criados em %s\n' "$DIST"
EOF
chmod +x "$ROOT/packaging/desktop/build-desktop-pkgs.sh"

cat > "$ROOT/packaging/desktop/README.md" <<'EOF'
# Pacotes de integração de desktop

O pacote `eazy` base é compatível com GNOME, KDE Plasma e outros ambientes. Os
metapacotes opcionais apenas declaram as ferramentas recomendadas para cada
desktop e dependem da mesma versão do pacote base:

```bash
sudo apt install ./eazy_3.3.1_all.deb
sudo apt install ./eazy-gnome_3.3.1_all.deb   # GNOME
sudo apt install ./eazy-kde_3.3.1_all.deb     # KDE Plasma
```

Eles não instalam uma segunda cópia do executável e podem ser removidos sem
apagar `~/.config/eazy`.
EOF

echo "Atualização de fontes concluída: eazy $VERSION"
