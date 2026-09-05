#!/usr/bin/env bash
# =============================================================================
#  eazy 3.2 — instalador para usuário final
#  https://github.com/vapesmadcat-blip/Easy_Player
#  Instala em ~/.local/bin — NÃO precisa de root/sudo
# =============================================================================
set -euo pipefail

VERSION="3.2"
BIN_DIR="${HOME}/.local/bin"
BASE_URL="https://raw.githubusercontent.com/vapesmadcat-blip/Easy_Player/c91e1859617135dc827bbe9110662ca79246a5b7/eazy"

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

mkdir -p "$BIN_DIR"
TMP=$(mktemp)
trap 'rm -f "$TMP"' EXIT

echo "  → Baixando eazy ${VERSION}..."
curl -fsSL "$BASE_URL" -o "$TMP"

if ! head -1 "$TMP" | grep -q '^#!'; then
  { printf '%s\n' '#!/usr/bin/env bash'; cat "$TMP"; } > "${TMP}.x"
  mv "${TMP}.x" "$TMP"
fi
chmod +x "$TMP"

if ! bash -n "$TMP" 2>/dev/null; then
  echo "  ✗ Download inválido. Tente de novo."
  exit 1
fi

cp -f "$TMP" "$BIN_DIR/eazy"
chmod +x "$BIN_DIR/eazy"

export PATH="$BIN_DIR:$PATH"
if [ -f "$HOME/.bashrc" ] && ! grep -q '\.local/bin' "$HOME/.bashrc" 2>/dev/null; then
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
  echo "  → PATH adicionado ao ~/.bashrc"
fi
if [ -f "$HOME/.zshrc" ] && ! grep -q '\.local/bin' "$HOME/.zshrc" 2>/dev/null; then
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
  echo "  → PATH adicionado ao ~/.zshrc"
fi

VER=$("$BIN_DIR/eazy" --version 2>/dev/null || echo "eazy ${VERSION}")
echo ""
echo "  ✓ Instalado em: $BIN_DIR/eazy"
echo "  ✓ $VER"
echo ""
echo "  Para usar AGORA:"
echo '      export PATH="$HOME/.local/bin:$PATH"'
echo "      eazy"
echo ""
echo "  (ou abra um terminal novo)"
echo ""
