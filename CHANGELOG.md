## 3.0-31 — Nome limpo das listas

- O Insert exibe somente o nome da lista e a quantidade de itens, ocultando o identificador interno.

## 3.0-30 — Retorno de diretórios em listas

- Diretórios nas listas temporárias aparecem como pastas.
- Entrar em uma pasta e pressionar `..` retorna à lista de origem.

## 3.0-29 — Diretórios nas listas temporárias

- Diretórios nas filas e listas personalizadas são reconhecidos como pastas, com tamanho recursivo e navegação.
- Diretórios não são enviados ao player como arquivos de mídia.

## 3.0-28 — Tab seleciona e avança

- Tab marca somente o item atual e avança para o próximo item.
- Espaço continua marcando no lugar.

## 3.0-27 — Seleção de diretórios e bytes

- Espaço e Tab selecionam arquivos e diretórios sem limpar a seleção.
- O cabeçalho mostra quantidade e bytes selecionados, com tamanho recursivo para diretórios.

## 3.0-26 — Rótulos das listas temporárias

- Insert e Ctrl-P mostram o nome real da lista e a quantidade de itens, sem C_ ou Fila 1.

## 3.0-25 — Nomes das listas temporárias

- Todas as listas personalizadas aparecem no Insert e no Ctrl-P com o nome informado.

## 3.0-24 — Listas temporárias no Ctrl-P

- Listas criadas pelo Insert agora aparecem no ciclo do Ctrl-P.

## 3.0-23 — Pesquisas salvas e listas temporárias

- Ctrl-S salva a pesquisa ativa com nome.
- Ctrl-F permite abrir uma pesquisa salva.
- Insert permite criar uma nova lista temporária nomeada.

## 3.0-22 — Retorno com posição persistente

- A posição salva é restaurada ao voltar pelo atalho, clique ou `Enter` em `..`.
- O mecanismo do fzf volta a usar o estado persistente original.

## 3.0-21 — Alertas sonoros

- Emite beep ao mudar de diretório.
- Emite beep nos diálogos de erro e falha.

## 3.0-20 — Posição do cursor na navegação

- Ctrl-Backspace restaura a posição salva do diretório anterior.
- Subir por `..` posiciona o cursor no topo, em `..`.

## 3.0-19 — Navegação e destinos persistentes

- Ao mudar de diretório, o filtro é limpo, o cursor vai para `..` e a seleção permanece.
- Os últimos destinos de copiar e mover ficam persistentes.

## 3.0-17 — Última nota editada

- O Ctrl-N agora abre sempre o último arquivo realmente salvo ou editado.
- A seleção, renomeação e criação de notas atualizam a persistência do último caminho.

## 3.0-16 — Mini editor visual de notas

- Substitui o editor baseado em Vim pelo mini editor visual Bash incluído no projeto.
- Mantém Ctrl-N para nova nota, Ctrl-S para salvar e abrir outra, Esc para salvar e sair, Enter para nova linha e Backspace para apagar.
- Preserva Ctrl-E, Ctrl-R e Ctrl-X para listar, renomear e exportar notas.

## 3.0-15 — Gerenciador de notas rápidas

- Ctrl-E abre uma lista compacta centralizada com as notas.
- Del apaga, Ctrl-R renomeia e Ctrl-X exporta para `~/Documentos/Easy-Notes/`.

## 3.0-14 — Editor de notas rápidas

- Ctrl-N abre a última nota ou cria `nota.txt`.
- Alt-N cria uma nova nota dentro do editor.
- Esc salva o conteúdo e sai do editor.

## 3.0-13 — Release eazy-v3.0-13

- Corrige o despacho de PDF antes do player MPlayer/mpv.
- PDF selecionado no navegador abre a caixa de leitura/conversão.
- Mantém a seleção fzf e a pausa de imagens.

## 3.0-12 — Release eazy-v3.0-12

- Suporte integrado para leitura e conversão de PDF.
- PDF abre pelo Enter; nenhuma opção D foi adicionada ao menu.
- Ferramentas: pdftotext, pdftohtml, pdftoppm e img2pdf.

## 3.0-11 — Release eazy-v3.0-11

- Instalação oficial por Release GitHub com pacote `.deb` e checksum `.sha256`.
- HELP EXPANDIDO atualizado com busca por `Esc`, DRY-RUN, sudo, progresso e temperatura da CPU.

# Changelog

## 3.0-11

- Restaurado o HELP EXPANDIDO do F10 com navegação, filas, duplicados, manutenção e dicas completas.
- `Esc` sai da busca recursiva e retorna à pasta normal sem fechar o eazy.
- Busca de duplicados com barra de progresso durante inventário, hashes e consolidação.
- Análise e limpeza automática de HD com progresso por etapas.
- Menu Ctrl-K ampliado com manutenção de sistema, HD, vídeo, som, SWAP e diretórios vazios.
- Nova opção de monitoramento de temperatura da CPU via `lm-sensors` e sensores térmicos do kernel.
- Operações que exigem sudo solicitam a senha em caixa antes da execução e usam `sudo -n` depois da autenticação.
- Estado do DRY-RUN exibido no cabeçalho e nas telas de manutenção.

## 3.0-10

- Filtro digitado (`FZF_QUERY`) permanece até mudar de pasta ou apagar
- Seleção no modo normal persiste em `SELECTED_FILE` (sobrevive a reload/filtro)
- Ctrl-A / Ctrl-R / Ctrl-X usam `eazy_sel_*` e não incluem `..`
- Ao mudar de pasta: zera seleção e limpa o filtro digitado

## 3.0-9

- Lista temporária dedicada para preservar seleções no modo Duplicados durante redesenhos
- Ctrl-R inverte a seleção atual; Ctrl-A seleciona todos e Ctrl-X limpa todos
- F12 mantém a seleção de um representante existente por grupo
- Enter, Insert, apagar, copiar, mover e embaralhar usam a seleção persistente
- Seleção permanece até Ctrl-X (zerar) ou mudança de pasta
- Ctrl-A / Ctrl-R não incluem a linha `..` / Voltar na seleção

## 3.0 — professional

- Identidade de versão e codinome
- `--help` em texto (estilo utilitário Unix)
- `--version` formal
- Instalador com lista clara de pacotes apt
- README e launcher `.desktop`
- Caminho como argumento reforçado (`eazy ~/Videos`)
- Filtro fzf estável (sem fzf aninhado no reload)
- `..` / Voltar sempre visíveis e fora da seleção em massa
- 3 filas temporárias (Ctrl-P / Insert)
- Alt-D apaga do disco em playlists; Del só remove da lista
- Marcação para exclusão no mpv (`d` / `D`)

## 2.3

- Persistência de sessão, cursor e preview
- Buffer de busca em sessão
- Múltiplos players e opção sem áudio

## 2.x

- Evolução iterativa: filas, busca, dups, downloads, ações
