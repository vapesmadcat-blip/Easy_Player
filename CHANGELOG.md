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
