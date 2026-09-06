#!/usr/bin/env bash
# =============================================================================
#  eazy 3.2 — instalador para usuário final
#  https://github.com/vapesmadcat-blip/Easy_Player
#  Instala em /usr/local/bin + atalho no menu (requer sudo)
# =============================================================================
set -euo pipefail

VERSION="3.2"
BIN_DIR="/usr/local/bin"
DESKTOP_DIR="/usr/share/applications"
BASE_URL="https://raw.githubusercontent.com/vapesmadcat-blip/Easy_Player/c91e1859617135dc827bbe9110662ca79246a5b7/eazy"

echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║   eazy ${VERSION} — instalador           ║"
echo "  ╚══════════════════════════════════════╝"
echo ""

for cmd in bash curl; do
  command -v "$cmd" >/dev/null 2>&1 || { echo "  ✗ Falta: $cmd"; exit 1; }
done
command -v sudo >/dev/null 2>&1 || { echo "  ✗ sudo não encontrado"; exit 1; }

TMP=$(mktemp)
trap 'rm -f "$TMP"' EXIT

echo "  → Baixando eazy ${VERSION}..."
curl -fsSL "$BASE_URL" -o "$TMP"

if ! head -1 "$TMP" | grep -q '^#!'; then
  { printf '%s\n' '#!/usr/bin/env bash'; cat "$TMP"; } > "${TMP}.x"
  mv "${TMP}.x" "$TMP"
fi
chmod +x "$TMP"
bash -n "$TMP" || { echo "  ✗ Arquivo inválido"; exit 1; }

echo "  → Instalando ${BIN_DIR}/eazy..."
sudo mkdir -p "$BIN_DIR"
sudo cp -f "$TMP" "${BIN_DIR}/eazy"
sudo chmod 755 "${BIN_DIR}/eazy"

# Atalho no menu de aplicações
echo "  → Instalando atalho (.desktop)..."
DESKTOP_TMP=$(mktemp)
cat > "$DESKTOP_TMP" << EOF
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
sudo cp -f "$DESKTOP_TMP" "${DESKTOP_DIR}/eazy.desktop"
sudo chmod 644 "${DESKTOP_DIR}/eazy.desktop"
rm -f "$DESKTOP_TMP"

if command -v update-desktop-database >/dev/null 2>&1; then
  sudo update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
fi

VER=$("${BIN_DIR}/eazy" --version 2>/dev/null || echo "eazy ${VERSION}")
echo ""
echo "  ✓ Binário:  ${BIN_DIR}/eazy"
echo "  ✓ Atalho:   ${DESKTOP_DIR}/eazy.desktop"
echo "  ✓ $VER"
echo ""
echo "  Atalhos de teclado (dentro do eazy):"
echo "    F9          Configuração"
echo "    F10         Ajuda"
echo "    Ctrl-F      Busca"
echo "    Ctrl-D      Duplicados"
echo "    Ctrl-K      Ações"
echo "    Ctrl-P      Filas"
echo "    Ctrl-A/X/R  Selecionar / limpar / inverter"
echo "    Q           Sair"
echo ""
echo "  Uso:  eazy"
echo ""
