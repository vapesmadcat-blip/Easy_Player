#!/usr/bin/env bash
set -Eeuo pipefail

VERSION="3.3.8"
BASE_URL="https://github.com/vapesmadcat-blip/Easy_Player/releases/download/eazy-v${VERSION}"
WORK_DIR="${TMPDIR:-/tmp}/eazy-install-${VERSION}-$$"
mkdir -p "$WORK_DIR"
trap 'rm -rf "$WORK_DIR"' EXIT

for cmd in sudo curl dpkg apt-get; do
  command -v "$cmd" >/dev/null 2>&1 || { echo "Erro: comando necessário não encontrado: $cmd" >&2; exit 1; }
done

if [ "$(id -u)" -eq 0 ]; then
  SUDO=""
else
  SUDO="sudo"
fi

DESKTOP="${XDG_CURRENT_DESKTOP:-${DESKTOP_SESSION:-}}"
case "${DESKTOP,,}" in
  *kde*|*plasma*) FLAVOR="kde" ;;
  *gnome*|*unity*|*cinnamon*) FLAVOR="gnome" ;;
  *) FLAVOR="" ;;
esac

fetch() {
  local name="$1"
  echo "Baixando $name..."
  curl -fL --retry 3 --connect-timeout 15 -o "$WORK_DIR/$name" "$BASE_URL/$name"
}

BASE_PACKAGE="eazy_${VERSION}_all.deb"
fetch "$BASE_PACKAGE"

if ! $SUDO dpkg -i "$WORK_DIR/$BASE_PACKAGE"; then
  echo "Corrigindo dependências do pacote base..."
  $SUDO apt-get -f install -y
fi

if [ -n "$FLAVOR" ]; then
  DESKTOP_PACKAGE="eazy-${FLAVOR}_${VERSION}_all.deb"
  fetch "$DESKTOP_PACKAGE"
  $SUDO apt-get install -y "$WORK_DIR/$DESKTOP_PACKAGE"
  echo "Integração $FLAVOR instalada."
else
  echo "Ambiente GNOME/KDE não detectado; instalando somente o pacote base."
  echo "Para escolher manualmente: eazy-gnome ou eazy-kde."
fi

if [ ! -r /dev/tty ]; then
  echo "Erro: execute o instalador em um terminal para informar a chave da IA." >&2
  exit 1
fi

printf 'Chave OpenRouter da IA (obrigatória): ' > /dev/tty
stty -echo < /dev/tty
read -r API_KEY < /dev/tty || API_KEY=""
stty echo < /dev/tty
printf '\n' > /dev/tty

if [ -z "$API_KEY" ]; then
  echo "Erro: nenhuma chave foi informada. A instalação foi interrompida." >&2
  exit 1
fi

mkdir -p "${XDG_CONFIG_HOME:-$HOME/.config}/eazy"
printf 'EAZY_AI_API_KEY=%s\n' "$API_KEY" > "${XDG_CONFIG_HOME:-$HOME/.config}/eazy/ai.env"
chmod 600 "${XDG_CONFIG_HOME:-$HOME/.config}/eazy/ai.env"
unset API_KEY
echo "Chave da IA salva com permissão 600."
hash -r 2>/dev/null || true
echo
echo "Instalação concluída: eazy $VERSION"
echo "Versão: eazy --version"
echo "Abrir IA: eazy --ai"
echo "Manual: man eazy"
