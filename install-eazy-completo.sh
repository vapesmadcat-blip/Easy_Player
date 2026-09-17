#!/usr/bin/env bash
set -e

echo "Cole sua chave OpenRouter e pressione Enter:"
if [ -r /dev/tty ]; then
  read -r -s -p "API key: " API_KEY < /dev/tty
else
  echo "Erro: execute o instalador em um terminal para informar a chave." >&2
  exit 1
fi
echo

if [ -z "$API_KEY" ]; then
  echo "Erro: nenhuma chave foi informada."
  exit 1
fi

mkdir -p "$HOME/.config/eazy"
printf 'EAZY_AI_API_KEY=%s\n' "$API_KEY" > "$HOME/.config/eazy/ai.env"
chmod 600 "$HOME/.config/eazy/ai.env"
unset API_KEY

PACKAGE="eazy_3.3_all.deb"
URL="https://github.com/vapesmadcat-blip/Easy_Player/releases/download/eazy-v3.3/$PACKAGE"
echo "Baixando eazy 3.3 com IA para ./..."
curl -fL --retry 3 -o "./$PACKAGE" "$URL"

echo "Instalando eazy completo com IA integrada..."
sudo apt-get install --reinstall -y "./$PACKAGE"

echo
echo "Instalação concluída."
echo "Teste com: eazy --version"
echo "Abra a IA com: eazy --ai"
