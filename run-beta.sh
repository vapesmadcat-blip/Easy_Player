#!/usr/bin/env bash
set -euo pipefail
EAZY_CALLER_CWD="$(pwd -P 2>/dev/null || pwd)"
export EAZY_CALLER_CWD
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
exec ./eazy "$@"
