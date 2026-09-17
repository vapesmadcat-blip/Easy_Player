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

echo "Baixando eazy 3.2.12 com IA..."
curl -fL --retry 3 \
  -o /tmp/eazy_3.2.12_all.deb \
  "https://github.com/vapesmadcat-blip/Easy_Player/releases/download/eazy-v3.2.12/eazy_3.2.12_all.deb"

echo "Instalando..."
sudo apt-get install -y /tmp/eazy_3.2.12_all.deb

echo
echo "Instalação concluída."
echo "Teste com: eazy --ai"
