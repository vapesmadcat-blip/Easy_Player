#!/usr/bin/env bash
# eazy 3.2 — SEM sudo → ~/.local/bin
# Baixa base + aplica patch de conversões (seleção)
set -euo pipefail
BIN="$HOME/.local/bin"
mkdir -p "$BIN"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
cd "$TMP"
echo ">> Baixando eazy 3.2..."
curl -fsSL "https://raw.githubusercontent.com/vapesmadcat-blip/Easy_Player/c91e1859617135dc827bbe9110662ca79246a5b7/eazy" -o eazy
echo ">> Baixando patch..."
curl -fsSL "https://raw.githubusercontent.com/vapesmadcat-blip/Easy_Player/main/eazy-conv-sel.patch" -o eazy-conv-sel.patch
# Se o patch do GitHub estiver quebrado, usa base pura
if patch -p1 --dry-run -i eazy-conv-sel.patch >/dev/null 2>&1; then
  patch -p1 -i eazy-conv-sel.patch
  echo ">> Patch de conversões aplicado"
else
  echo ">> Aviso: patch não aplicou; instalando base 3.2 (ainda funciona)"
fi
if ! head -1 eazy | grep -q '^#!'; then
  { echo '#!/usr/bin/env bash'; cat eazy; } > eazy.x && mv eazy.x eazy
fi
chmod +x eazy
cp -f eazy "$BIN/eazy"
chmod +x "$BIN/eazy"
grep -q '.local/bin' "$HOME/.bashrc" 2>/dev/null || echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
export PATH="$BIN:$PATH"
echo
echo "OK: $($BIN/eazy --version)"
echo
echo "Nesta sessão:"
echo '  export PATH="$HOME/.local/bin:$PATH"'
echo "  eazy"
