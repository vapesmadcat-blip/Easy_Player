#!/usr/bin/env bash
# Instala eazy a partir desta pasta do repositório
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -f ./eazy ]; then
  echo "Arquivo ./eazy não encontrado nesta pasta." >&2
  exit 1
fi
chmod +x ./eazy
exec ./eazy --install "$@"
