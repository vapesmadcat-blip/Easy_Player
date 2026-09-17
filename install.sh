#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
chmod +x eazy eazy-notes-editor 2>/dev/null || true
./eazy --install
