#!/usr/bin/env bash
# =============================================================================
#  eazy 3.2 — instalador para usuário final
#  https://github.com/vapesmadcat-blip/Easy_Player
#  Instala em /usr/local/bin (requer sudo)
# =============================================================================
set -euo pipefail

VERSION="3.2"
BIN_DIR="/usr/local/bin"
BASE_URL="https://raw.githubusercontent.com/vapesmadcat-blip/Easy_Player/c91e1859617135dc827bbe9110662ca79246a5b7/eazy"
DESKTOP_DIR="/usr/share/applications"
ICON_DIR="/usr/share/icons/hicolor/256x256/apps"

echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║   eazy ${VERSION} — instalador           ║"
echo "  ╚══════════════════════════════════════╝"
echo ""

for cmd in bash curl; do
  command -v "$cmd" >/dev/null 2>&1 || {
    echo "  ✗ Falta o comando: $cmd"
    exit 1
  }
done

if ! command -v sudo >/dev/null 2>&1; then
  echo "  ✗ sudo não encontrado. Instale com permissões de administrador."
  exit 1
fi

TMP=$(mktemp)
trap 'rm -f "$TMP"' EXIT

echo "  → Baixando eazy ${VERSION}..."
curl -fsSL "$BASE_URL" -o "$TMP"

# shebang na 1ª linha (evita "exec format error")
if ! head -1 "$TMP" | grep -q '^#!'; then
  { printf '%s\n' '#!/usr/bin/env bash'; cat "$TMP"; } > "${TMP}.x"
  mv "${TMP}.x" "$TMP"
fi
chmod +x "$TMP"

if ! bash -n "$TMP" 2>/dev/null; then
  echo "  ✗ Download inválido. Tente de novo."
  exit 1
fi

echo "  → Instalando em ${BIN_DIR}/eazy (sudo)..."
sudo mkdir -p "$BIN_DIR"
sudo cp -f "$TMP" "${BIN_DIR}/eazy"
sudo chmod 755 "${BIN_DIR}/eazy"

# .desktop (opcional, se o repo tiver)
DESKTOP_TMP=$(mktemp)
if curl -fsSL "https://raw.githubusercontent.com/vapesmadcat-blip/Easy_Player/main/eazy.desktop" -o "$DESKTOP_TMP" 2>/dev/null; then
  # Força Exec e Terminal corretos
  if ! grep -q '^Exec=' "$DESKTOP_TMP"; then
    echo 'Exec=/usr/local/bin/eazy' >> "$DESKTOP_TMP"
  else
    sed -i 's|^Exec=.*|Exec=/usr/local/bin/eazy|' "$DESKTOP_TMP"
  fi
  if ! grep -q '^Terminal=' "$DESKTOP_TMP"; then
    echo 'Terminal=true' >> "$DESKTOP_TMP"
  else
    sed -i 's|^Terminal=.*|Terminal=true|' "$DESKTOP_TMP"
  fi
  sudo mkdir -p "$DESKTOP_DIR"
  sudo cp -f "$DESKTOP_TMP" "${DESKTOP_DIR}/eazy.desktop"
  sudo chmod 644 "${DESKTOP_DIR}/eazy.desktop"
  echo "  → Atalho: ${DESKTOP_DIR}/eazy.desktop"
fi
rm -f "$DESKTOP_TMP"

# Atualiza cache de apps se disponível
if command -v update-desktop-database >/dev/null 2>&1; then
  sudo update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
fi

VER=$("${BIN_DIR}/eazy" --version 2>/dev/null || echo "eazy ${VERSION}")
echo ""
echo "  ✓ Instalado em: ${BIN_DIR}/eazy"
echo "  ✓ $VER"
echo ""
echo "  Uso:"
echo "      eazy"
echo ""
