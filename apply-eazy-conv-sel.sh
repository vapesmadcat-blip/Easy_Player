#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
[ -f eazy ] || { echo "Falta eazy neste diretório"; exit 1; }
[ -f eazy-conv-sel.patch ] || { echo "Falta eazy-conv-sel.patch"; exit 1; }
cp -a eazy "eazy.bak-conv-$(date +%Y%m%d%H%M%S)"
patch -p1 -i eazy-conv-sel.patch
chmod +x eazy
echo "OK: Conversões (Ctrl-K → C) usam os arquivos selecionados."
echo "Instalar: sudo cp eazy /usr/local/bin/eazy"
