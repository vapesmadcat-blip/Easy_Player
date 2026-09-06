#!/usr/bin/env bash
# eazy 3.2 COMPLETO — Hotkeys no F9 | sudo → /usr/local/bin
set -euo pipefail
VERSION="3.2"
BIN="/usr/local/bin/eazy"
BASE="https://raw.githubusercontent.com/vapesmadcat-blip/Easy_Player/c91e1859617135dc827bbe9110662ca79246a5b7/eazy"
INJECT="https://raw.githubusercontent.com/vapesmadcat-blip/Easy_Player/main/inject-hotkeys.py"

echo ""
echo "  eazy ${VERSION} COMPLETO (Hotkeys)"
echo ""

command -v sudo >/dev/null || { echo "precisa sudo"; exit 1; }
command -v curl >/dev/null || { echo "precisa curl"; exit 1; }
command -v python3 >/dev/null || { echo "precisa python3"; exit 1; }

TMPD=$(mktemp -d)
trap 'rm -rf "$TMPD"' EXIT
cd "$TMPD"

echo "  → Baixando eazy..."
curl -fsSL "$BASE" -o eazy

echo "  → Baixando injetor Hotkeys..."
curl -fsSL "$INJECT" -o inject-hotkeys.py

echo "  → Aplicando Hotkeys..."
python3 inject-hotkeys.py eazy

if ! head -1 eazy | grep -q '^#!'; then
  { printf '%s\n' '#!/usr/bin/env bash'; cat eazy; } > eazy.x && mv eazy.x eazy
fi
chmod +x eazy
bash -n eazy
grep -q configurar_hotkeys eazy || { echo "Falha: Hotkeys não aplicados"; exit 1; }

echo "  → Instalando $BIN ..."
sudo cp -f eazy "$BIN"
sudo chmod 755 "$BIN"

cat > eazy.desktop << 'DEOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=eazy
Exec=/usr/local/bin/eazy %F
TryExec=/usr/local/bin/eazy
Icon=multimedia-player
Terminal=true
Categories=AudioVideo;Player;
DEOF
sudo cp -f eazy.desktop /usr/share/applications/eazy.desktop
sudo chmod 644 /usr/share/applications/eazy.desktop

echo ""
echo "  ✓ $($BIN --version)"
echo "  ✓ F9 → Hotkeys (atalhos de teclado)"
echo ""
