#!/usr/bin/env bash
set -euo pipefail
REPO="vapesmadcat-blip/Easy_Player"
VERSION="3.10.1"
TAG="eazy-v${VERSION}"
ASSET="eazy-${VERSION}-corrigido"
URL="https://github.com/${REPO}/releases/download/${TAG}/${ASSET}"
TMP_DIR="$(mktemp -d)"
BIN_PATH="${TMP_DIR}/eazy"
cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT
if [[ "${EUID}" -eq 0 ]]; then
  SUDO=""
else
  SUDO="sudo"
fi

echo "Baixando eazy ${VERSION}..."
if command -v curl >/dev/null 2>&1; then
  curl -fL --retry 3 --connect-timeout 15 -o "$BIN_PATH" "$URL"
elif command -v wget >/dev/null 2>&1; then
  wget -O "$BIN_PATH" "$URL"
else
  echo "Erro: instale curl ou wget e tente novamente." >&2
  exit 1
fi

chmod 755 "$BIN_PATH"
if ! bash -n "$BIN_PATH"; then
  echo "Erro: o arquivo baixado não é um eazy válido." >&2
  exit 1
fi

echo "Instalando eazy ${VERSION}..."
$SUDO install -Dm755 "$BIN_PATH" /usr/bin/eazy
$SUDO install -Dm755 "$BIN_PATH" /usr/lib/eazy/eazy

# Mantém também a cópia do usuário, quando ~/.local/bin estiver disponível.
USER_HOME="${SUDO_USER:+$(getent passwd "$SUDO_USER" | cut -d: -f6)}"
USER_HOME="${USER_HOME:-$HOME}"
install -Dm755 "$BIN_PATH" "$USER_HOME/.local/bin/eazy" 2>/dev/null || true

echo
echo "eazy ${VERSION} instalado com sucesso."
echo "Versão: $(/usr/bin/eazy --version 2>/dev/null || true)"
echo "Execute: eazy"
