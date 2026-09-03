#!/usr/bin/env bash
# Instala eazy 3.2 a partir desta pasta do repositório
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -f ./eazy ]; then
  echo "Arquivo ./eazy não encontrado nesta pasta." >&2
  exit 1
fi
# Aplica patch 3.2 se ainda estiver em versão antiga
if grep -q 'EAZY_VERSION="3.0' ./eazy 2>/dev/null && [ -f ./eazy-3.2.patch ]; then
  echo "Aplicando eazy-3.2.patch..."
  patch -p1 --forward < ./eazy-3.2.patch || true
fi
chmod +x ./eazy
exec ./eazy --install "$@"
