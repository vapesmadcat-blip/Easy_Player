<<<<<<< HEAD
## 3.2.4 — HTML/URL no browser + revisão no cabeçalho

- Enter em HTML/HTM e links `http(s)` abre o browser (`xdg-open` / `gio` / Firefox / Chromium).
- Usa caminho absoluto e `file://`; não envia HTML ao player de mídia.
- Cabeçalho do script: `Revisão 3.2.4` e `EAZY_VERSION="3.2.4"`.
- Mantidos: Del/Shift+Del, lixeira (F9), export notas (F9), prune da seleção global, filtros com extensões.

=======
>>>>>>> e75456e8ed3e5762134030cdfe70cacc19dde9b9
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
- Sem teclas `ctrl-shift-delete` / `alt-shift-delete` no expect do fzf (compatível com fzf antigo).

## 3.2.3 — Ctrl+A respeita o filtro

- Corrigido o Ctrl+A para selecionar somente os itens atualmente visíveis no filtro.
- Mantida a seleção global de itens em outras pastas.
- Atualizado o pacote Debian para a versão 3.2.3.
