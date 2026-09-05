#!/bin/bash
# ==============================================================================
# Compilador Seguro e Corrigido para o Utilitário Eazy
# Resolve o bug do BASH_SOURCE[0] criando um ciclo de execução seguro
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

echo -e "\033[1;36m[1/4]\033[0m Codificando o script Eazy em Base64..."
SCRIPT_B64=$(base64 -w 0 "$SCRIPT_ORIGINAL")

echo -e "\033[1;36m[2/4]\033[0m Gerando o Wrapper em C com correção de ciclo de execução..."
cat << EOF > "$ARQUIVO_C"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>

const char* b64_script = "${SCRIPT_B64}";

int main(int argc, char *argv[]) {
    // Cria um arquivo temporário físico real para que o BASH_SOURCE[0] funcione
    char tmp_path[] = "/tmp/.ez_runtime_XXXXXX";
    int fd = mkstemp(tmp_path);
    if (fd == -1) {
        fprintf(stderr, "Erro crítico: Não foi possível instanciar o ambiente temporário.\n");
        return 1;
    }
    close(fd);

    // Escreve o script decodificado no arquivo oculto temporário
    char cmd_decode[512];
    snprintf(cmd_decode, sizeof(cmd_decode), "echo \"%s\" | base64 -d > %s", b64_script, tmp_path);
    if (system(cmd_decode) != 0) {
        unlink(tmp_path);
        return 1;
    }

    // Garante as permissões de execução do script temporário
    chmod(tmp_path, S_IRUSR | S_IWUSR | S_IXUSR);

    // Calcula o tamanho dinâmico para a string final do comando com todos os argumentos
    size_t cmd_size = strlen(tmp_path) + 32;
    for (int i = 1; i < argc; i++) {
        cmd_size += strlen(argv[i]) + 4;
    }

    char *exec_cmd = (char *)malloc(cmd_size);
    if (exec_cmd == NULL) {
        unlink(tmp_path);
        return 1;
    }

    // Prepara a chamada mantendo a integridade dos argumentos ($@)
    snprintf(exec_cmd, cmd_size, "%s", tmp_path);
    for (int i = 1; i < argc; i++) {
        strcat(exec_cmd, " \"");
        strcat(exec_cmd, argv[i]);
        strcat(exec_cmd, "\"");
    }

    // Executa o script de forma nativa e transparente para o fzf/mpv
    int status = system(exec_cmd);

    // Destrói o arquivo temporário imediatamente após fechar o programa
    unlink(tmp_path);
    free(exec_cmd);

    if (status == -1) {
        return 1;
    }
    return WEXITSTATUS(status);
}
EOF

echo -e "\033[1;36m[3/4]\033[0m Compilando nativamente com GCC aplicando otimizações..."
gcc -O2 "$ARQUIVO_C" -o "$BINARIO_FINAL"

if [ ! -f "$BINARIO_FINAL" ]; then
    echo -e "\033[1;31m[ERRO] Falha na compilação do GCC.\033[0m"
    rm -f "$ARQUIVO_C"
    exit 1
fi

echo -e "\033[1;36m[4/4]\033[0m Removendo tabelas de símbolos (Stripping)..."
strip --strip-all "$BINARIO_FINAL"

# Limpeza dos resíduos de build
rm -f "$ARQUIVO_C"

echo -e "\n\033[1;32m✓ COMPILAÇÃO CONCLUÍDA COM SUCESSO!\033[0m"
echo -e "Execute agora o seu novo binário protegido: \033[1;37m./$BINARIO_FINAL\033[0m\n"
