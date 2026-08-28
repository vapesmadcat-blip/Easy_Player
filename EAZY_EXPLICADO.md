# eazy — navegador e player multimídia no terminal

## Visão geral

O **eazy** é um navegador multimídia para terminal escrito em Bash e construído em torno do `fzf`. Ele permite localizar, organizar, reproduzir, converter, copiar, mover e administrar arquivos de áudio, vídeo, imagens, PDFs e documentos sem abandonar o ambiente do terminal.

A proposta central é transformar o sistema de arquivos em uma interface navegável, rápida e controlada por teclado. O programa também mantém o estado da sessão, as filas temporárias, as notas, as pesquisas salvas, os destinos de operações e a posição do cursor.

> O eazy combina navegação de arquivos, reprodução multimídia, manutenção do sistema e organização pessoal em uma única interface interativa.

## Como funciona

Ao iniciar, o eazy lê a configuração do usuário, recupera a última sessão e abre o diretório salvo. A listagem é ordenada conforme o modo escolhido, possui preview opcional e apresenta informações de tamanho, tipo e estado do item.

O `fzf` funciona como núcleo da navegação. O usuário pode filtrar a lista, marcar vários arquivos ou diretórios, entrar em pastas, voltar pelo item `..`, trocar de diretório, alterar a ordenação e executar ações diretamente pelos atalhos. A seleção múltipla é usada pelas operações de reprodução, cópia, movimentação, exclusão, filas e conversão.

A seleção por `Tab` marca o item atual e avança para o próximo; `Espaço` marca ou desmarca o item sem avançar. O cabeçalho mostra o total de itens e os bytes selecionados. Em diretórios, o tamanho é calculado recursivamente.

## Reprodução e formatos

O eazy reconhece arquivos de áudio, vídeo, imagens, PDFs, textos e playlists. O player pode usar `mpv`, `mplayer`, VLC ou `ffplay`, conforme a configuração. Imagens podem ser visualizadas com preview e pausa; PDFs podem ser lidos como texto, convertidos para HTML ou transformados em imagens PNG.

O sistema de conversões permite trabalhar com vídeo, imagens e PDF, incluindo conversão de imagens para PDF e de PDF para imagens. A escolha dos arquivos ocorre por seleção na interface, evitando a necessidade de digitar caminhos manualmente.

## Filas e listas temporárias

O eazy mantém três filas temporárias e permite criar listas adicionais nomeadas pelo menu `Insert`. As listas personalizadas aparecem no `Insert` e no ciclo do `Ctrl-P` usando o nome informado pelo usuário e a quantidade de itens.

Diretórios inseridos em uma lista são reconhecidos como pastas. Eles aparecem com ícone de diretório, podem ser abertos com `Enter`, têm o tamanho calculado recursivamente e não são enviados ao player como se fossem arquivos de mídia. Ao sair de uma pasta aberta a partir de uma lista, o eazy retorna à lista de origem.

## Pesquisa e organização

A busca pode usar extensão, faixa de tamanho e conteúdo. Pesquisas podem ser salvas com um nome e reutilizadas posteriormente. O sistema de duplicados identifica arquivos repetidos, permite amostragem por grupo, seleção visual e ações sobre os itens selecionados.

As operações de copiar e mover mantêm o último destino utilizado. Isso reduz repetição e torna práticas as rotinas de organização de grandes coleções.

## Notas rápidas

O editor de notas rápidas abre a última nota editada e mantém o conteúdo salvo. Ele inclui criação de novas notas, lista compacta, renomeação, exclusão e exportação para `~/Documentos/Easy-Notes/`.

O editor visual não depende de Vim, vi ou nano e utiliza os atalhos definidos pelo projeto: `Ctrl-N` para nova nota, `Ctrl-S` para salvar e abrir outra, `Esc` para salvar e sair, `Enter` para nova linha e `Backspace` para apagar.

## Manutenção e segurança

O menu de manutenção reúne diagnósticos de sistema, disco, SMART, memória SWAP, temperatura da CPU, áudio, vídeo, rede e ferramentas disponíveis. Operações privilegiadas solicitam a senha em uma caixa própria e exibem o estado do modo **DRY-RUN** antes de executar alterações.

O modo DRY-RUN permite revisar comandos destrutivos ou administrativos sem modificar o sistema. O eazy também verifica espaço disponível antes de operações que podem consumir armazenamento e informa falhas com mensagens visíveis e alerta sonoro do terminal.

## Persistência e estrutura de dados

Os dados do usuário ficam em `~/.config/eazy`, sem serem removidos quando o pacote é desinstalado. A estrutura principal é:

| Caminho | Finalidade |
|---|---|
| `~/.config/eazy/config` | Preferências do programa |
| `~/.config/eazy/notas/` | Notas rápidas |
| `~/.config/eazy/saved_searches/` | Pesquisas salvas |
| `~/.config/eazy/temp_playlist_1` a `_3` | Três filas temporárias |
| `~/.config/eazy/temp_playlist_custom_*` | Listas temporárias nomeadas |
| `~/.config/eazy/last_copy_destination` | Último destino de cópia |
| `~/.config/eazy/last_move_destination` | Último destino de movimentação |
| `~/.config/eazy/dir_positions` | Posições persistentes do cursor |
| `~/Documentos/Easy-Notes/` | Notas exportadas |
| `~/Playlists/` | Playlists salvas pelo usuário |

## Vantagens

A principal vantagem do eazy é a integração. Em vez de alternar entre gerenciadores de arquivos, players, ferramentas de busca, conversores e scripts de manutenção, o usuário acessa essas funções em uma mesma interface.

A navegação por teclado reduz movimentos repetitivos e é adequada para coleções grandes. A seleção múltipla, as filas, as pesquisas salvas e os destinos persistentes aceleram tarefas recorrentes. O preview, a identificação por ícones, os indicadores de tamanho e o cabeçalho de seleção tornam a interface mais informativa.

A persistência da sessão evita perder o contexto de trabalho. O usuário pode sair e retornar depois encontrando o diretório, a posição e as listas no estado esperado. O tratamento especial de diretórios evita confundir pastas com mídia e torna as listas mais úteis para organização.

A arquitetura em Bash favorece portabilidade, transparência e facilidade de auditoria. O código pode ser lido, ajustado e executado em distribuições Linux com ferramentas tradicionais, enquanto o pacote Debian simplifica a instalação e a integração com o sistema.

## Instalação

A instalação pelo script verifica o gerenciador de pacotes disponível, instala as ferramentas principais e auxiliares de reprodução, conversão, preview, PDF, diagnóstico e compactação. Também instala o comando global, o editor de notas e o launcher desktop, quando disponível.

```bash
./eazy --install
```

Para instalações Debian publicadas, use o pacote da Release correspondente e confirme o checksum antes de instalar.

## Resumo dos principais atalhos

| Atalho | Função |
|---|---|
| `Tab` | Seleciona o item e avança |
| `Espaço` | Seleciona ou desmarca sem avançar |
| `Enter` | Abre, reproduz ou entra no item |
| `Ctrl-P` | Alterna filas e listas |
| `Insert` | Envia seleção para uma fila ou cria lista |
| `Ctrl-Y` | Copia a seleção |
| `Ctrl-U` | Move a seleção |
| `Ctrl-N` | Abre a última nota |
| `Ctrl-K` | Ações e manutenção |
| `F10` | Ajuda expandida |

## Conclusão

O eazy foi projetado para quem trabalha com muitos arquivos multimídia e deseja velocidade, controle e previsibilidade. Ele une reprodução, pesquisa, organização, conversão, diagnóstico e anotações rápidas, preservando o contexto de trabalho e reduzindo a dependência de múltiplas aplicações.

A combinação de interface de terminal, seleção múltipla, persistência, DRY-RUN, filas nomeadas e suporte a diretórios torna o eazy uma ferramenta prática para administrar bibliotecas pessoais, diretórios de trabalho e coleções multimídia.

---

**Projeto:** Easy_Player  
**Comando:** `eazy`  
**Documentação:** `README.md`, `INSTALL.md`, `CHANGELOG.md` e este arquivo

## Referências

[1]: https://github.com/vapesmadcat-blip/Easy_Player "Repositório oficial do Easy_Player"

O código-fonte e as versões publicadas estão disponíveis no [repositório oficial do projeto][1].

