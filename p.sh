#!/usr/bin/env bash

# Arquivo onde a seleção será salva
ARQUIVO_SEL="${TMPDIR:-/tmp}/fzf_selecao_automatica"
touch "$ARQUIVO_SEL"

# 1. Gerar a lista combinada (Coloca os já salvos no topo com um indicador '*')
gerar_lista() {
    # Exibe os arquivos já salvos anteriormente com o marcador '*'
    if [ -s "$ARQUIVO_SEL" ]; then
        awk '{print "* " $0}' "$ARQUIVO_SEL"
    fi
    # Exibe todos os arquivos do diretório atual tirando os que já estão salvos
    find . -type f | sed 's|^\./||' | grep -vFf "$ARQUIVO_SEL"
}

# Exporta a função para que o fzf possa usá-la se necessário
export -f gerar_lista
export ARQUIVO_SEL

# 2. Executa o fzf
# --ansi permite colorir se desejar
# --multi ativa a seleção múltipla com TAB
SELECAO=$(gerar_lista | fzf \
    --multi \
    --prompt="Arquivos (Inicie com TAB para alterar marcas): " \
    --header="[TAB] Marcar/Desmarcar | [Enter] Salvar e Sair" \
    --no-sort)

# Se o usuário cancelou com ESC ou Ctrl+C, mantém o arquivo antigo e sai
[ -z "$SELECAO" ] && exit 0

# 3. Processa e Salva Automaticamente no Enter
# Remove o indicador '* ' dos itens que vieram do topo e limpa linhas vazias
echo "$SELECAO" | sed 's/^\* //' | grep -v '^$' > "$ARQUIVO_SEL"

echo "=== Seleção salva automaticamente em $ARQUIVO_SEL ==="
cat "$ARQUIVO_SEL"
