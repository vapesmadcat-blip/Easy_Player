#!/usr/bin/env bash
# eazy 3.2 PRONTO — SEM sudo → ~/.local/bin
# Conversões usam arquivos selecionados (Ctrl-K → C)
set -euo pipefail
URL="https://raw.githubusercontent.com/vapesmadcat-blip/Easy_Player/main"
TMPD=$(mktemp -d)
trap 'rm -rf "$TMPD"' EXIT
echo ">> Baixando eazy 3.2 PRONTO..."
for i in $(seq 0 11); do
  curl -fsSL "$URL/eazy.b64.$i" -o "$TMPD/eazy.b64.$i" || {
    echo "Erro ao baixar eazy.b64.$i"
    exit 1
  }
done
TMP=$(mktemp)
for i in $(seq 0 11); do cat "$TMPD/eazy.b64.$i"; done | base64 -d | gzip -d > "$TMP"
chmod +x "$TMP"
mkdir -p "$HOME/.local/bin"
cp -f "$TMP" "$HOME/.local/bin/eazy"
chmod +x "$HOME/.local/bin/eazy"
grep -q '.local/bin' "$HOME/.bashrc" 2>/dev/null || echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
export PATH="$HOME/.local/bin:$PATH"
echo "OK: $($HOME/.local/bin/eazy --version)"
echo
echo "Nesta sessão:"
echo '  export PATH="$HOME/.local/bin:$PATH"'
echo "  eazy"
