#!/usr/bin/env bash
#
# eazy-notes-editor — Editor de notas v3.2
# Com painel de atalhos visível à direita da janela
#

CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/eazy"
NOTES_DIR="$CONFIG_DIR/notas"
LAST_NOTE_FILE="$NOTES_DIR/.ultima_nota"

# Cores
BOLD='\033[1m'
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
WHITE='\033[1;37m'
RESET='\033[0m'
DIM='\033[2m'

mkdir -p "$NOTES_DIR" 2>/dev/null || true

NOTE_FILE="${1:-$NOTES_DIR/nota.txt}"

# Função para renderizar o editor com painel de atalhos
render_editor() {
    local content="$1"
    local cols lines
    
    cols=$(tput cols)
    lines=$(tput lines)
    
    # Dimensões: editor ocupa 65% | painel ocupa 35%
    local editor_width=$((cols * 65 / 100 - 2))
    local panel_width=$((cols - editor_width - 3))
    local editor_height=$((lines - 4))
    
    clear
    
    # ═══ CABEÇALHO ═══
    printf "${BOLD}${CYAN}"
    printf "╔═"
    printf "%0.s═" $(seq 1 $((cols - 4)))
    printf "═╗\n"
    printf "║ EDITOR DE NOTAS v3.2 - $(basename "$NOTE_FILE") │ Tamanho: ${YELLOW}${#content}${CYAN} chars"
    printf "%0.s " $(seq 1 $((cols - 60)))
    printf "║\n"
    printf "╠═"
    printf "%0.s═" $(seq 1 $((editor_width + 1)))
    printf "╦"
    printf "%0.s═" $(seq 1 $((panel_width)))
    printf "╣\n${RESET}"
    
    # ═══ ÁREA DE EDIÇÃO + PAINEL ═══
    local line_num=0
    while IFS= read -r line || [ -n "$line" ]; do
        line_num=$((line_num + 1))
        if [ $line_num -le $editor_height ]; then
            # Editor (esquerda)
            printf "║ %-${editor_width}s ║ " "${line:0:$editor_width}"
            
            # Painel de atalhos (direita)
            case $line_num in
                1)  printf "${YELLOW}Ctrl-N${RESET} ${DIM}Nova nota${RESET}" ;;
                2)  printf "${YELLOW}Ctrl-S${RESET} ${DIM}Salva e nova${RESET}" ;;
                3)  printf "${YELLOW}Ctrl-E${RESET} ${DIM}Lista notas${RESET}" ;;
                4)  printf "${YELLOW}Ctrl-I${RESET} ${DIM}Importar${RESET}" ;;
                5)  printf "${YELLOW}Ctrl-R${RESET} ${DIM}Renomeia${RESET}" ;;
                6)  printf "${YELLOW}Ctrl-X${RESET} ${DIM}Exporta${RESET}" ;;
                7)  printf "${YELLOW}Esc${RESET}    ${DIM}Salva/Sai${RESET}" ;;
                8)  printf "${YELLOW}Enter${RESET}  ${DIM}Nova linha${RESET}" ;;
                9)  printf "${YELLOW}Backsp${RESET} ${DIM}Apaga${RESET}" ;;
                10) printf "${YELLOW}Ctrl-A${RESET} ${DIM}Seleciona${RESET}" ;;
                11) printf "${YELLOW}F1${RESET}     ${DIM}Ajuda${RESET}" ;;
                *)  printf "" ;;
            esac
            
            printf "║\n"
        fi
    done <<< "$content"
    
    # Preencher linhas vazias
    while [ $line_num -lt $editor_height ]; do
        line_num=$((line_num + 1))
        printf "║ %-${editor_width}s ║ %-${panel_width}s ║\n" "" ""
    done
    
    # ═══ RODAPÉ ═══
    printf "${BOLD}${CYAN}"
    printf "╠═"
    printf "%0.s═" $(seq 1 $((editor_width + 1)))
    printf "╩"
    printf "%0.s═" $(seq 1 $((panel_width)))
    printf "╣\n"
    printf "║ ${WHITE}[Esc]${CYAN}=Salva  ${WHITE}[Ctrl-N]${CYAN}=Nova  ${WHITE}[Ctrl-S]${CYAN}=Salva  ${WHITE}[Ctrl-E]${CYAN}=Lista  ${WHITE}[F1]${CYAN}=Ajuda"
    printf "%0.s " $(seq 1 $((cols - 75)))
    printf "║\n"
    printf "╚═"
    printf "%0.s═" $(seq 1 $((cols - 4)))
    printf "═╝${RESET}\n"
}

# Editor interativo
edit_note() {
    local file="$1"
    local content
    
    [ -f "$file" ] || touch "$file"
    content=$(cat "$file" 2>/dev/null || echo "")
    
    while true; do
        render_editor "$content"
        
        # Input interativo
        IFS= read -rsn1 key
        
        case "$key" in
            $'\e')  # ESC
                echo -n "$content" > "$file"
                echo "$file" > "$LAST_NOTE_FILE" 2>/dev/null || true
                clear
                printf "${GREEN}✓ Nota salva: $(basename "$file")${RESET}\n"
                return 0
                ;;
            $'\x7f'|$'\b')  # BACKSPACE
                content="${content%?}"
                ;;
            $'\n'|$'\r')  # ENTER
                content="${content}
"
                ;;
            '')  # Ctrl-A (seleciona tudo)
                content="$content"
                ;;
            '')  # Ctrl-E (lista notas)
                clear
                printf "${CYAN}Lista de notas:${RESET}\n"
                ls -1 "$NOTES_DIR" 2>/dev/null | head -10
                printf "\nPressione Enter para continuar...\n"
                read -rsn1
                ;;
            '')  # Ctrl-I (importar)
                clear
                printf "${CYAN}Importar notas de arquivo${RESET}\n"
                printf "Digite o caminho do arquivo: "
                read -r import_file
                if [ -f "$import_file" ]; then
                    import_content=$(cat "$import_file")
                    content="${content}${import_content}"
                    printf "${GREEN}✓ Importado${RESET}\n"
                    sleep 1
                fi
                ;;
            '')  # Ctrl-N (nova nota)
                echo -n "$content" > "$file"
                clear
                printf "${CYAN}Criar nova nota${RESET}\n"
                printf "Nome: "
                read -r new_name
                if [ -n "$new_name" ]; then
                    file="$NOTES_DIR/$new_name"
                    [ -f "$file" ] || touch "$file"
                    content=""
                    echo "$file" > "$LAST_NOTE_FILE" 2>/dev/null || true
                fi
                ;;
            '')  # Ctrl-R (renomear)
                clear
                printf "${CYAN}Renomear nota${RESET}\n"
                printf "Novo nome: "
                read -r new_name
                if [ -n "$new_name" ]; then
                    new_file="$NOTES_DIR/$new_name"
                    mv "$file" "$new_file" 2>/dev/null
                    file="$new_file"
                    echo "$file" > "$LAST_NOTE_FILE" 2>/dev/null || true
                    printf "${GREEN}✓ Renomeado${RESET}\n"
                    sleep 1
                fi
                ;;
            '')  # Ctrl-S (salva e nova)
                echo -n "$content" > "$file"
                clear
                printf "${CYAN}Criar nova nota${RESET}\n"
                printf "Nome: "
                read -r new_name
                if [ -n "$new_name" ]; then
                    file="$NOTES_DIR/$new_name"
                    [ -f "$file" ] || touch "$file"
                    content=""
                    echo "$file" > "$LAST_NOTE_FILE" 2>/dev/null || true
                fi
                ;;
            '')  # Ctrl-X (exportar)
                echo -n "$content" > "$file"
                clear
                printf "${CYAN}Exportar para ~/Documentos/Easy-Notes/${RESET}\n"
                mkdir -p ~/Documentos/Easy-Notes 2>/dev/null || true
                export_file="$HOME/Documentos/Easy-Notes/$(basename "$file")"
                cp "$file" "$export_file"
                printf "${GREEN}✓ Exportado: $export_file${RESET}\n"
                read -rsn1
                ;;
            '')  # F1 (ajuda)
                clear
                cat << 'HELP'
╔════════════════════════════════════════════════════════════════╗
║             EDITOR DE NOTAS v3.2 — AJUDA COMPLETA             ║
╚════════════════════════════════════════════════════════════════╝

EDIÇÃO:
  • Escrever normalmente — texto inserido em tempo real
  • Enter — quebra linha
  • Backspace — apaga caractere anterior

ARQUIVO:
  • Ctrl-N — criar nova nota
  • Ctrl-S — salvar e abrir outra
  • Ctrl-R — renomear nota
  • Ctrl-X — exportar para ~/Documentos/Easy-Notes/
  • Ctrl-E — listar todas as notas
  • Ctrl-I — importar de arquivo externo

FINALIZAR:
  • Esc — salvar e sair
  • Ctrl-C — cancelar

RECURSOS v3.2:
  ✓ Painel de atalhos sempre visível
  ✓ Quebra de linha automática
  ✓ Importar/exportar notas
  ✓ Sem dependência de Vim/Nano

Pressione qualquer tecla para voltar...
HELP
                read -rsn1
                ;;
            *)
                content="${content}${key}"
                ;;
        esac
    done
}

# MAIN
if [ ! -d "$NOTES_DIR" ]; then
    mkdir -p "$NOTES_DIR" || exit 1
fi

if [ -n "$1" ] && [ -f "$1" ]; then
    edit_note "$1"
    exit $?
fi

if [ -f "$LAST_NOTE_FILE" ]; then
    NOTE_FILE=$(cat "$LAST_NOTE_FILE" 2>/dev/null)
fi

edit_note "$NOTE_FILE"
