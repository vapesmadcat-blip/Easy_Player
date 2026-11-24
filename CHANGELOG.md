## 5.2.0 rev.48 — decisões de conflito antes da cópia

- A simulação apresenta cada colisão antes de qualquer escrita e usa as mesmas opções da rev.46: renomear automaticamente, sobrescrever, pular este item e continuar, pular os conflitos restantes ou cancelar.
- As decisões são guardadas no plano da cópia. Após a confirmação final, a cópia real não abre diálogos de conflito; se o destino mudar inesperadamente após a simulação, a operação para por segurança sem perguntar no meio.
- Testes cobrem decisões distintas em conflitos separados, `skip_all`, cancelamento da simulação e recusa da confirmação final, verificando que não há prompts durante a execução real.

## 5.2.0 rev.47 — seleção SQL explícita e prévia de cópia

- Ctrl+Y/Ctrl+U no navegador normal preservam a seleção amarela (`selected=1`) até a decisão; se existir seleção global (`selected=2`), mostram a quantidade e oferecem usar somente a seleção atual ou unir também a global.
- Ctrl+K mantém a mesma decisão quando a ação escolhida é copiar ou mover. Listas, pesquisa, downloads e Duplicados não são alterados por essa regra.
- Antes de copiar, mostra uma prévia com itens, tamanho estimado, espaço livre e conflitos previstos; permite renomear, sobrescrever, pular todos, cancelar ou manter as perguntas individuais por conflito.
- A suíte de cópia testa conflitos previstos, decisões em lote e cancelamento antes da escrita; testes SQLite cobrem contagem, escolha local, união opcional e preservação dos estados `1` e `2`.

## 5.2.0 rev.46 — cópia segura de árvores

- Preserva a hierarquia dos caminhos selecionados ao copiar diretórios e não mescla árvores distintas só porque têm pastas com o mesmo nome.
- Em conflitos, oferece renomeação automática, sobrescrita explícita, pular o item e continuar, pular os conflitos restantes ou cancelar.
- Recusa destinos dentro da origem e testa hierarquia, colisões, cancelamento e proteção contra cópia sobre a própria origem.

## 5.2.0 rev.45 — navegação, seleção e Ctrl+K

- Ao entrar em uma pasta coberta por monitor ativo, pula a assinatura MD5 rasa somente se já houver assinatura indexada, o backend estiver pronto e a fila não tiver eventos; qualquer incerteza ou ticket pendente mantém a reconciliação normal.
- A alternância SQL da seleção retorna as estatísticas no mesmo comando; o cabeçalho reutiliza o resultado durante a sessão FZF em vez de relançar consultas a cada atualização.
- Ctrl+K prioriza somente os itens amarelos imediatos do diretório atual, sem promover nem consumir seleção global. Sem amarelos, usa somente o arquivo sob o cursor; opções sem alvo de arquivo (manutenção, sistema, swap e similares) continuam disponíveis.
- Reduz subprocessos no cálculo da contagem do menu Ctrl+K e na alternância de seleção de pastas.
- Verificado com testes sintéticos de seleção global/local, cursor, descendentes, alternância de arquivos/pastas e fila do monitor; a medição local do sandbox não substitui teste de tempo real no WSL/DrvFs.

## 5.2.0 rev.44 — escopo de pastas, curingas e filtros em listas

- A pesquisa e a identificação de duplicados usam a união das pastas marcadas globalmente; sem pastas marcadas, preservam a pasta atual. A exclusão da configuração do Easy permanece aplicada.
- A pesquisa SQLite e o fallback aceitam curingas de nome (`vid*`, `movie.*`, `*.mp4`) junto com extensões literais, inclusive quando “DIGITAR” é a única opção marcada.
- F4–F7 aplicam o filtro de categoria ao conteúdo de playlists, filas e histórico. O cache da lista leva o filtro em conta e arquivos genéricos como `.txt` não são mais classificados como vídeo.
- Alinha o filtro de vídeo do navegador para incluir `.mpg`, `.mpeg` e `.m2ts`.

## 5.2.0 rev.43 — lista de raízes monitoradas no F9

- O F9 mantém uma lista persistente de diretórios, com ações para adicionar, remover, iniciar e parar uma raiz individual, ou iniciar/parar todas.
- Cada raiz usa diretório de estado e fila exclusivos; raízes iguais ou sobrepostas são recusadas para evitar monitores duplicados e tickets cruzados.
- Um monitor legado ativo é transferido para a lista quando o menu é aberto, preservando a opção de itens ocultos.
- A parada remove um `full` órfão somente quando o executável corresponde exatamente ao binário privado daquela raiz; não usa `killall full` nem encerra outros programas com o mesmo nome.
- Antes de atualizar o SQLite pelo F9, os monitores cadastrados ativos são parados; após sucesso ou falha, as mesmas raízes são reativadas.
- Mantém os backends Linux/inotify e Windows/FileSystemWatcher existentes, sem executar instaladores.

## 5.2.0 rev.42 — confirmação de arquivos novos em /mnt no WSL2

- O `FileSystemWatcher` marca criações de arquivos como evento próprio; no WSL2, confirma a entrada ativa no SQLite e repete a sincronização rasa da pasta se DrvFs ainda não expôs o novo caminho na primeira leitura.
- A lógica nova só roda para eventos de criação do watcher Windows; o backend e o comportamento de atualização no sistema de arquivos Linux permanecem inalterados.

## 5.2.0 rev.41 — eventos em unidades Windows no WSL2

- Para raízes em `/mnt/<unidade>`, acrescenta `FileSystemWatcher` nativo do Windows ao monitor C `/s /start`; ambos encaminham eventos ao mesmo fluxo SQLite/refresh, sem varredura periódica da árvore.
- Para raízes Linux, mantém o monitor recursivo C/inotify da rev.40; o indexador SQLite permanece inalterado.

## 5.2.0 rev.40 — monitor recursivo em tempo real

- Integra o monitor C inotify com fila privada de tickets NUL-delimitados e preserva `/h`, `/o`, `/s` e `/start`; o F9 escolhe a raiz recursiva e decide se inclui itens ocultos.
- Sincroniza pais afetados com SQLite e percorre árvores novas; tickets permanecem na fila até todas as operações do indexador terem sucesso.
- Quando suportado pelo FZF, `--listen` pede a recarga imediata da pasta ativa; sem listener, a próxima alteração de filtro consome o marcador. Não há consulta ao banco a cada tecla.
- Instala e distribui `eazy-live-watch.py` e `full.c`; não altera em escopo amplo o armazenamento de temporários.

## 5.2.0 rev.39 — aviso durante a abertura

- Mostra no terminal as etapas de preparação do SQLite, conferência da pasta inicial e montagem da primeira lista, para indicar atividade durante a abertura.
- Limpa o aviso antes do FZF e não o exibe em modos não interativos ou de manutenção.

## 5.2.0 rev.38 — exclusão segura e limpeza do histórico

- No Histórico, Delete, Shift+Delete e Alt+D removem somente uma ou várias entradas SQLite; nenhum desses atalhos apaga arquivos de mídia.
- Adiciona ao F9 a opção “Limpar histórico”, com confirmação, removendo apenas os registros SQLite e preservando os arquivos físicos e o histórico legado.

## 5.2.0 rev.37 — preservação dos arquivos de cache

- Invalida caches de listagem por geração, preservando os arquivos `.lst` e `.meta` existentes em vez de apagá-los.
- Mantém a atualização F9 com progresso explícito durante a conferência de registros antigos no SQLite.

## 5.2.0 rev.36 — progresso da limpeza SQLite no F9

- Mostra a etapa que confere registros antigos e marca itens removidos, com contador e pasta examinada, evitando a aparência de travamento em 99%.
- Mantém o painel PTY ancorado no mesmo lugar e identifica explicitamente se o caminho exibido é item, diretório ou pasta em conferência.

## 5.2.0 rev.35 — painel PTY e atualização incremental por diretório

- Substitui o gauge do F9 por uma tela PTY com etapa, atividade, pasta inicial, caminho atual, tempo e progresso real.
- Na atualização geral, calcula e salva no SQLite uma assinatura MD5 da listagem imediata de cada diretório.
- Nas próximas atualizações, percorre as pastas para conferir suas assinaturas e evita enviar ao atualizador de linhas os arquivos de diretórios inalterados; pastas descendentes continuam sendo verificadas para detectar mudanças profundas.
- O percurso usa um walker Python único, reaproveita metadados coletados e exclui a configuração do Easy.

## 5.2.0 rev.34 — atualização de índice visível e proteção da configuração

- F9 inicia por padrão na pasta atual, exibe o ponto de partida confirmado e mostra progresso desde a enumeração até o processamento SQLite.
- Atualização e pesquisas ignoram a pasta de configuração efetiva do eazy; consultas também filtram entradas antigas e resultados em cache.
- Protege a árvore de configuração (e seus ancestrais) contra exclusão física iniciada por seleção, playlist ou marcação do player.

## 5.2.0 rev.33 — reprodução de listas e parâmetros dos players

- F12 reproduz a lista ativa; Ctrl+E embaralha a lista ativa sem alterar a ordem persistida.
- Preserva F12 para amostragem no modo Duplicados e mantém o shuffle anterior fora de listas.
- Com `EXIT_DIR_MODE=navegador` e sessão salva, reabre na pasta do navegador em vez do diretório chamador.
- Permite configurar argumentos extras por player (mpv, MPlayer, cvlc e ffplay), interpretados como argumentos separados sem `eval`.

## 5.2.0 rev.32 — `.ts` tratado como TypeScript

- Remove `.ts` das extensões reconhecidas, filtradas e coletadas como vídeo.
- Arquivos `.ts` passam a aparecer como arquivos genéricos, sem associação ao grupo de vídeos.
- Reclassifica uma única vez no SQLite arquivos `.ts` antigos que estavam marcados como vídeo, sem forçar recatalogação de diretórios intactos.

## 5.2.0 rev.31 — assinatura rápida de diretórios e identificação em borda

- Mostra a versão no canto inferior direito da borda do fzf, sem ocupar o cabeçalho.
- Compara uma assinatura MD5 determinística dos metadados dos itens ao reentrar em cada diretório; só atualiza registros do índice quando a assinatura muda.
- Mantém a otimização de preview sob demanda e o acumulador de seleção.

## 5.2.0 rev.30 — preview sob demanda e identificação visível

- Mostra `eazy 5.2.0 rev.30` no cabeçalho do navegador, na saída do Ctrl-Q e em `eazy --version`.
- Evita executar leitura detalhada de preview quando desativado e reduz consultas SQLite repetidas ao digitar o filtro.
- Preserva as estatísticas/acumulador de seleção e a interoperabilidade das playlists M3U.

## 5.2.0 — persistência local SQLite para filas e listas temporárias

- Migra as filas 1–3 e listas personalizadas do armazenamento permanente em arquivos para tabelas SQLite individuais no banco local.
- Inclui `migrate_eazy_lists.py`, com prévia, transações, backup do banco e preservação dos arquivos antigos durante a migração.
- Faz Ctrl+P e criação, inclusão, remoção, validação e reprodução de listas consultarem o catálogo e as tabelas SQLite; os arquivos temporários são apenas snapshots efêmeros de compatibilidade.
- Usa lookup de arquivos em lote ao abrir listas e sincroniza diretórios incrementalmente quando a assinatura de conteúdo muda.
- Preserva a migração do histórico SQLite, corrigida na 5.1.3, e mantém o arquivo de histórico legado intacto.
- Corrige a resolução do nome lógico no cabeçalho de listas SQL e registra a revisão de teste no `--version`.
- Atualiza Help TXT/HTML, man page, instaladores e artefatos de distribuição para 5.2.0.

## 5.1.3 — migração segura do histórico SQLite

- Reconstrói `history_items` diretamente do arquivo legado, preservando ordem, caracteres e a origem intacta.
- Usa a mesma barreira de migração em Ctrl+G e Ctrl+P → Histórico; contagens, caminhos e metadados vêm do SQLite.
- Corrige a leitura de timestamps pelo shell e inclui `eazy-index.py` nos instaladores e pacotes.

## 5.0.0 — Central de streaming integrada
- Restaura o seletor de navegador do easiea ao abrir o Help HTML e arquivos HTML.
- Usa o `easiea` enviado como base, preservando melhorias de seleção, exportação, manutenção e diagnóstico.
- Integra o `eazy-yt-stream` com pesquisa persistente, histórico de filmes assistidos, pergunta de favorito ao terminar, favoritos, duração dos vídeos e paginação de 30 resultados.
- Inclui o stream, IA, editor de notas, eazy-tor, man page e help no instalador e no pacote Debian.
- Remove o caminho fixo `/home/jim` do empacotamento e mantém os componentes em `/usr/bin` e `/usr/lib/eazy`.

## 3.2.10 — Enter py/sh/html com menu (estilo PDF)
- Ramo principal do Enter chama menu_arquivo_* para py, sh e html.

## 3.2.9 — Menus numerados
## 3.2.8 — Alt-X qtd/bytes
## 3.2.7 — SHELL_CMD e menus sh/html
## 3.2.6 — PYTHON_CMD
