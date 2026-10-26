# Validação Easy 5.0.0

A base usada foi o arquivo `easiea` enviado para esta release. A versão foi alterada para `5.0.0` e o componente `eazy-yt-stream` foi integrado ao menu de streams, ao comando `eazy --stream`, ao instalador e ao pacote Debian.

## Passou

A sintaxe Bash passou para `eazy`, `eazy-yt-stream`, `eazy-tor`, `eazy-notes-editor`, os instaladores e o construtor Debian. `eazy --version` retorna `eazy 5.0.0 (help-html)`. A ajuda principal contém `--stream`, `--update-all`, `--install` e manutenção; a ajuda do stream contém pesquisa de filmes.

O pacote Debian foi construído com sucesso e contém `eazy`, `eazy-yt-stream`, `eazy-ai.py`, `eazy-tor`, `eazy-notes-editor`, launcher desktop, man page e help TXT/HTML. A inspeção do conteúdo confirmou ausência de `/home/jim` e de arquivos instalados na raiz do pacote. O ZIP completo contém também o executável Dev Linux x86_64.

O executável Dev foi recompilado com `tools/compilar-eazy.sh` e retorna `eazy 5.0.0`. O checksum gerado foi `0548b54f95ead8b8a65c2f2bc026e4e7ef6bc1c7aec9c45ccc57d96ec4effc26`.

A presença do cliente de IA, editor, Tor, manutenção completa, `update-all`, instalador global e instalador local sem sudo foi verificada por sintaxe e inspeção de caminhos. O `update-all` atualiza os pacotes declarados por cada gerenciador e baixa o binário oficial mais recente do yt-dlp; não foi executado no ambiente de validação para não alterar o sistema do build.

## Testes legados

O teste de playlist passou. Alguns testes antigos de seleção/help não foram considerados bloqueadores porque extraem funções por números de linha ou procuram textos exatos da base anterior; a base `easiea` reorganiza essas funções e altera os cabeçalhos. A sintaxe e as verificações funcionais específicas da release 5.0.0 passaram.
