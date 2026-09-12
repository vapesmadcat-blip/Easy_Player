## 3.2.3 — Lixeira, HTML, prune da seleção, Del e filtros

- **Del** apaga somente o item sob o cursor; **Shift+Del** pergunta seleção local ou global (em duplicados usa a seleção amarela).
- Após apagar do disco, a seleção global (`selected_paths`) é atualizada e caminhos inexistentes são removidos (`eazy_prune_selecao_global`).
- Itens apagados são retirados da playlist/fila aberta e da seleção amarela de duplicados.
- **F9 → Abrir lixeira** entra em `~/.local/share/Trash/files`.
- **F9 → Exportar notas** copia notas para `~/Documentos/Easy-Notes/`.
- **Enter** em `.html` / `.htm` e em URLs `http(s)` abre no browser via `xdg-open`.
- Filtros Videos / Audios / Imgs / Compactados exibem as extensões no prompt.
- Diálogo de zerar seleção global informa quantidade de arquivos e tamanho em bytes.
- Ctrl+A continua a selecionar somente os itens visíveis no filtro ativo.
- Sem `ctrl-shift-delete` / `alt-shift-delete` no expect do fzf (compatível com fzf antigo).

## 3.2.3 — Ctrl+A respeita o filtro
- Corrigido o Ctrl+A para selecionar somente os itens atualmente visíveis no filtro.
- Mantida a seleção global de itens em outras pastas.
- Atualizado o pacote Debian para a versão 3.2.3.

## 3.0-62 — Navegação e manutenção avançada

- `Home` vai ao primeiro item e `End` ao último item das listas, inclusive filas temporárias.
- A seleção normal não é descartada automaticamente após ações; o usuário a remove desmarcando os itens.
- Adicionado `eazy -a`, com lista única segmentada por PLAYLISTS, LISTAS TEMPORÁRIAS, DUPLICADOS, PESQUISAS SALVAS, NOTAS, HISTÓRICO/DOWNLOADS e ESTADO/BACKUPS.
- A manutenção avançada mostra preview de conteúdo, calcula espaço, respeita DRY-RUN e registra exclusões em ordem, data, hora, tamanho e caminho completo.

## 3.0-62 — Guia rápido e manutenção revisada

- Adicionado o GUIA_RAPIDO.md com exemplos práticos de busca por curingas, conteúdo, frases e operadores.
- Limpezas agora exibem cálculo de espaço também no DRY-RUN.
- Comandos de limpeza limpam a tela antes da execução e pausam depois do resultado.
- Filtros restaurados são sanitizados contra CR e sequências ANSI residuais.
- Revisada a preservação da seleção e conferida a lista de dependências do instalador.

## 3.0-60 — Documentação consolidada da busca avançada

- Atualizada toda a documentação da pesquisa por extensões, nomes e curingas.
- Documentadas palavras múltiplas, frases entre aspas e operadores `AND`, `OR` e `NOT`.
- Mantidos os recursos de manutenção, snapshots, validação, notas e limpeza segura das versões anteriores.

## 3.0-59 — Manutenção Linux e pausas no menu

- Corrigido o modo `eazy -m` para executar somente depois que todas as funções de manutenção foram carregadas.
- Adicionada limpeza da tela antes do início da limpeza automática, após a prévia e a confirmação final.
- O menu de ações agora pausa ao final de cada ação para que o resultado de aplicativos externos possa ser lido.

## 3.0-58 — Limpeza automática com prévia e idade configurável

- A limpeza automática agora pergunta quantos dias devem ser usados como critério.
- A prévia informa quantos logs, temporários e itens da lixeira são elegíveis.
- Nenhuma limpeza começa antes da visualização da prévia e de uma confirmação final.
- O critério escolhido é aplicado a logs, journal, temporários e lixeira.
- O modo DRY-RUN continua impedindo a remoção real.
