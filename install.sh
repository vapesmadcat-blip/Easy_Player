#!/usr/bin/env bash
# eazy 3.2 — instalador (sudo → /usr/local/bin)
# F9 → Hotkeys | atalho .desktop
set -euo pipefail

VERSION="3.2"
BIN_DIR="/usr/local/bin"
DESKTOP_DIR="/usr/share/applications"
BASE_URL="https://raw.githubusercontent.com/vapesmadcat-blip/Easy_Player/c91e1859617135dc827bbe9110662ca79246a5b7/eazy"
PATCH_URL="https://raw.githubusercontent.com/vapesmadcat-blip/Easy_Player/main/eazy-hotkeys.patch"

echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║   eazy ${VERSION} — instalador           ║"
echo "  ╚══════════════════════════════════════╝"
echo ""

for cmd in bash curl; do
  command -v "$cmd" >/dev/null 2>&1 || { echo "  ✗ Falta: $cmd"; exit 1; }
done
command -v sudo >/dev/null 2>&1 || { echo "  ✗ sudo não encontrado"; exit 1; }

TMPD=$(mktemp -d)
trap 'rm -rf "$TMPD"' EXIT
cd "$TMPD"

echo "  → Baixando eazy ${VERSION}..."
curl -fsSL "$BASE_URL" -o eazy

echo "  → Aplicando Hotkeys (item no F9)..."
if curl -fsSL "$PATCH_URL" -o eazy-hotkeys.patch 2>/dev/null && patch -p1 --dry-run -i eazy-hotkeys.patch >/dev/null 2>&1; then
  patch -p1 -i eazy-hotkeys.patch
  echo "  → Hotkeys OK"
else
  echo "  → Aviso: patch hotkeys não aplicado (base instalada)"
fi

if ! head -1 eazy | grep -q '^#!'; then
  { printf '%s\n' '#!/usr/bin/env bash'; cat eazy; } > eazy.x && mv eazy.x eazy
fi
chmod +x eazy
bash -n eazy

echo "  → Instalando ${BIN_DIR}/eazy..."
sudo mkdir -p "$BIN_DIR"
sudo cp -f eazy "${BIN_DIR}/eazy"
sudo chmod 755 "${BIN_DIR}/eazy"

echo "  → Atalho .desktop..."
DT=$(mktemp)
cat > "$DT" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=eazy
GenericName=Terminal Media Browser
Comment=Navegador e player multimídia no terminal (fzf + mpv)
Exec=/usr/local/bin/eazy %F
TryExec=/usr/local/bin/eazy
Icon=multimedia-player
Terminal=true
Categories=AudioVideo;Player;Filesystem;
Keywords=media;video;audio;fzf;mpv;files;eazy;
StartupNotify=false
MimeType=inode/directory;video/*;audio/*;
EOF
sudo mkdir -p "$DESKTOP_DIR"
sudo cp -f "$DT" "${DESKTOP_DIR}/eazy.desktop"
sudo chmod 644 "${DESKTOP_DIR}/eazy.desktop"
rm -f "$DT"
command -v update-desktop-database >/dev/null 2>&1 && sudo update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true

echo ""
echo "  ✓ ${BIN_DIR}/eazy"
echo "  ✓ ${DESKTOP_DIR}/eazy.desktop"
echo "  ✓ $(${BIN_DIR}/eazy --version 2>/dev/null || echo eazy ${VERSION})"
echo ""
echo "  Menu F9:"
echo "    • Configurar o eazy"
echo "    • Hotkeys (atalhos de teclado)   ← novo"
echo "    • Overview do sistema"
echo "    • Teste de som"
echo ""
echo "  Config hotkeys: ~/.config/eazy/keys"
echo ""
