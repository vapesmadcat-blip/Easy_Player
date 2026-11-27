# Guia rápido do eazy

## Iniciar

Execute `eazy` para abrir o navegador. Use `Enter` para entrar em pastas ou abrir arquivos, `Tab` para selecionar e avançar, `Espaço` para selecionar sem avançar e `Esc` para cancelar uma operação interrompível.

## Espaço livre no cabeçalho

O indicador **HD livre/total** mostra primeiro o espaço disponível e depois a capacidade total do filesystem que contém a pasta navegada. Em `/mnt/c/...`, consulta o mount de `/mnt/c`; em `/home/...`, consulta o filesystem de `/home`.

## Apagar (3.2.3)

| Tecla | Efeito |
|--------|--------|
| **Del** | Só o arquivo sob o cursor |
| **Shift+Del** | Pergunta **local** (tela) ou **global** (todas as pastas). Nos **duplicados**, usa a seleção **amarela** |
| **Alt-D** | Apagar do disco com a seleção de ações |

Ao apagar do disco, o eazy remove os caminhos de `~/.config/eazy/selected_paths`, da playlist/fila aberta e da seleção amarela de duplicados.

## HTML, links e lixeira

- **Enter** em `.html` / `.htm` ou em URL `http://` / `https://` abre no browser (`xdg-open`).
- **F9 → Abrir lixeira** entra em `~/.local/share/Trash/files`.
- **F9 → Exportar notas** copia `~/.config/eazy/notas/` para `~/Documentos/Easy-Notes/`.

## Filtros com extensões

O prompt mostra as extensões do filtro ativo, por exemplo:

- `videos (mp4/mkv/avi/webm/mov…)`
- `audios (mp3/m4a/flac/wav…)`
- `imgs (jpg/png/gif/webp…)`
- `compactados (zip/7z/rar/tar…)`

## Pesquisa por nome e extensão

Pressione `Ctrl-F`. O campo aceita vários padrões separados por espaço ou vírgula:

```text
sh mp4 vid* filme.mov movie.*
```

| Padrão | Significado |
|---|---|
| `sh` | Arquivos com extensão `.sh` |
| `mp4` | Arquivos com extensão `.mp4` |
| `vid*` | Nomes que começam com `vid` |
| `filme.mov` | Nome específico `filme.mov` |
| `movie.*` | Nomes que começam com `movie.` e qualquer extensão |

## Busca por conteúdo

Na etapa de conteúdo, escolha **Sim — digitar uma ou mais palavras-chave**. A busca não diferencia maiúsculas de minúsculas e é aplicada somente depois do filtro por nome/extensão.

Palavras separadas por espaço significam `AND`. Use `OR`, `NOT` e frases entre aspas conforme a documentação completa.

## Seleção e filas

Use `Insert` para enviar itens às filas 1, 2 ou 3. `Ctrl-P` alterna entre as filas e a pasta. Em listas com múltiplos itens, `Tab` seleciona e avança; `Espaço` marca o item mantendo o cursor no mesmo lugar.

Ao marcar um diretório com `Espaço` ou `Tab`, o indicador **Dir** do cabeçalho mostra o tamanho total dos arquivos dentro dele e das subpastas, sem somar o tamanho técnico das pastas.

Ao **zerar a seleção global**, o diálogo mostra a **quantidade de arquivos** e o **tamanho total** em bytes.

## Manutenção e DRY-RUN

Use `eazy -m`, `eazy -a` ou o menu `Ctrl-K`. Em `Ctrl-K → Z`, revise diretórios vazios e arquivos regulares de 0 bytes antes de confirmar; a raiz pesquisada é preservada e diretórios são removidos com `rmdir`, sem recursão. O modo **DRY-RUN** mostra o que seria feito sem remover dados.

## Parâmetros extras dos players

Em **F9 → Players e parâmetros extras**, escolha mpv, MPlayer, VLC/cvlc ou ffplay. Depois selecione **Editar o valor atual** (campo preenchido), **Substituir por uma nova linha** (campo vazio) ou **Remover todos os parâmetros deste player**. As chaves são salvas em `~/.config/eazy/config`.

O guia completo está em [`EAZY_EXPLICADO.md`](EAZY_EXPLICADO.md).
