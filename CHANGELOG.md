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
