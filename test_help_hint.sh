#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
# Cada ramo do construtor de lista deve anunciar F10 antes dos demais atalhos.
awk '
  /EAZY_HEADER_HINT=/ { seen++ ; if ($0 !~ /\[F10\]: Ajuda/) { print "F10 ausente: " $0 > "/dev/stderr"; bad=1 } }
  END { if (seen != 8 || bad) { print "esperados 8 cabeçalhos com F10; encontrados " seen > "/dev/stderr"; exit 1 } }
' "$ROOT/eazy"
grep -Fq 'elif [ "$tecla" = "f10" ]; then' "$ROOT/eazy"
printf 'help-hint: OK\n'
