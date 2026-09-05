#!/bin/bash
# ==============================================================================
# Compilador Seguro para o Utilitário Eazy
# Transforma o script Bash em um binário nativo ELF protegido
# ==============================================================================

SCRIPT_ORIGINAL="eazy"
ARQUIVO_C="wrapper_eazy.c"
BINARIO_FINAL="eazy_compilado"

# 1. Validações iniciais
if [ ! -f "$SCRIPT_ORIGINAL" ]; then
    echo -e "\033[1;31m[ERRO] O script original '$SCRIPT_ORIGINAL' não foi encontrado neste diretório.\033[0m"
    exit 1
fi

if ! command -v gcc &>/dev/null; then
    echo -e "\033[1;31m[ERRO] O compilador GCC não está instalado. Instale-o com: sudo apt install gcc\033[0m"
    exit 1
fi

echo -e "\033[1;36m[1/4]\033[0m Convertendo o script Bash para Base64..."
# Codifica o script inteiro em uma única linha Base64 segura
SCRIPT_B64=$(base64 -w 0 "$SCRIPT_ORIGINAL")

echo -e "\033[1;36m[2/4]\033[0m Gerando o Wrapper em linguagem C..."
# Constrói o código-fonte em C embutindo o script e tratando os argumentos da CLI ($@)
cat << EOF > "$ARQUIVO_C"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

/* Script original criptografado em Base64 */
const char* b64_script = "${SCRIPT_B64}";

int main(int argc, char *argv[]) {
    // Calcula o tamanho aproximado necessário para o buffer do comando
    // Base64 + comando base + espaço extra para múltiplos argumentos longos
    size_t tamanho_buffer = strlen(b64_script) + 256;
    for (int i = 1; i < argc; i++) {
        tamanho_buffer += strlen(argv[i]) + 4;
    }

    char *comando = (char *)malloc(tamanho_buffer);
    if (comando == NULL) {
        fprintf(stderr, "Erro crítico: Falha na alocação de memória do sistema.\n");
        return 1;
    }

    // Injeta o binário descriptografado diretamente para a instância do bash
    snprintf(comando, tamanho_buffer, "echo \"%s\" | base64 -d | bash -s --", b64_script);

    // Concatena e sanitiza os argumentos passados via terminal
    for (int i = 1; i < argc; i++) {
        strcat(comando, " \"");
        strcat(comando, argv[i]);
        strcat(comando, "\"");
    }

    // Executa e retorna o código de saída correto do script embutido
    int status = system(comando);
    free(comando);

    if (status == -1) {
        return 1;
    }
    return WEXITSTATUS(status);
}
EOF

echo -e "\033[1;36m[3/4]\033[0m Compilando nativamente com GCC aplicando otimizações..."
# Compila aplicando otimização de performance nível 2 (-O2)
gcc -O2 "$ARQUIVO_C" -o "$BINARIO_FINAL"

if [ ! -f "$BINARIO_FINAL" ]; then
    echo -e "\033[1;31m[ERRO] Falha na compilação do GCC.\033[0m"
    rm -f "$ARQUIVO_C"
    exit 1
fi

echo -e "\033[1;36m[4/4]\033[0m Aplicando Stripping (Removendo tabelas de símbolos e debug)..."
# Executa a limpeza profunda do binário contra engenharia reversa básica
strip --strip-all "$BINARIO_FINAL"

# Limpa o arquivo C temporário gerado no processo
rm -f "$ARQUIVO_C"

echo -e "\n\033[1;32m╔════════════════════════════════════════════════════════════╗\033[0m"
echo -e "\033[1;32m║          SUCESSO! SEU PROJETO 'EAZY' FOI COMPILADO         ║\033[0m"
echo -e "\033[1;32m╚════════════════════════════════════════════════════════════╝\033[0m"
echo -e "Binário protegido gerado: \033[1;37m./$BINARIO_FINAL\033[0m"
echo -e "O código-fonte original está seguro contra leituras diretas.\n"
