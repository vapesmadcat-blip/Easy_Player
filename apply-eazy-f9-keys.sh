#!/usr/bin/env bash
# Aplica suporte a atalhos configuráveis (F9 → Atalhos) no eazy
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
[ -f eazy ] || { echo "Execute na pasta do repositório Easy_Player (arquivo eazy)."; exit 1; }
[ -f eazy-f9-keys.patch ] || { echo "Falta eazy-f9-keys.patch"; exit 1; }
cp -a eazy "eazy.bak-f9-keys-$(date +%Y%m%d%H%M%S)"
patch -p1 -i eazy-f9-keys.patch
chmod +x eazy
echo "OK. Atalhos: F9 → Atalhos de teclado"
echo "Arquivo: ~/.config/eazy/keys"
echo "Para instalar no sistema: sudo cp eazy /usr/local/bin/eazy && sudo chmod +x /usr/local/bin/eazy"
