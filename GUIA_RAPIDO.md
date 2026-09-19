# Guia rápido do eazy 3.8.1

## Iniciar

Execute `eazy` para abrir o navegador. Use `Enter` para entrar em pastas ou abrir arquivos, `Tab` para selecionar e avançar, `Espaço` para selecionar sem avançar e `Esc` para cancelar uma operação interrompível.

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

Ao **zerar a seleção global**, o diálogo mostra a **quantidade de arquivos** e o **tamanho total** em bytes.

## Manutenção e DRY-RUN

Use `eazy -m`, `eazy -a` ou o menu `Ctrl-K`. O modo **DRY-RUN** mostra o que seria feito sem remover dados.

O guia completo está em [`EAZY_EXPLICADO.md`](EAZY_EXPLICADO.md).

## Instalar pacotes `.deb` com Enter

Navegue até um arquivo `.deb` e pressione **Enter**. O eazy mostra nome, versão e descrição, pede confirmação e chama o APT para instalar o pacote. A instalação requer confirmação explícita.

## Formato e cores da lista

A informação aparece como **TAM · DATA · TIPO**. As cores seguem o ciclo visual **idx3** de três cores por posição da linha; isso é apenas uma marca visual e não indica diferença entre vídeos.

## Ajuda e manual

Use `eazy --help` para a ajuda no terminal, `F10` para a ajuda interativa e `man eazy` para a referência completa.


## Destino dos downloads

Por padrão, downloads feitos pelo Ctrl-B são salvos em `~/Downloads`. Altere em **F9 → Configurar → Pasta Padrão de Downloads**. O eazy cria a pasta automaticamente e mostra o destino ao iniciar o download.


## Downloaders, Tor e parâmetros

Em **F9 → Downloads — downloader, Tor e parâmetros**, escolha aria2c, Axel, wget ou yt-dlp, ative opcionalmente Tor (`socks5://127.0.0.1:9050`) e informe parâmetros extras. O default para links diretos continua sendo **aria2c**; o Axel usa **`--insecure -n 4`** por padrão. A configuração fica em `~/.config/eazy/config`.


## Tor e torsocks

O instalador `eazy --install` inclui `tor` e `torsocks` quando o sistema oferece esses pacotes. Manualmente, use `sudo apt update && sudo apt install tor torsocks -y` (Debian/Ubuntu/Mint), `sudo dnf install tor torsocks -y` (Fedora/RHEL) ou `sudo pacman -S tor torsocks` (Arch). Inicie com `sudo systemctl start tor` e, se desejar, `sudo systemctl enable tor`.

Ao adicionar um link, marque **Usar Tor neste download**. O eazy usa SOCKS5 em `127.0.0.1:9050`. Para testar: `torsocks curl https://icanhazip.com`. Para aria2c, Axel e wget, o eazy usa `torsocks` automaticamente quando o checkbox está marcado. Teste separadamente com `torsocks curl https://icanhazip.com`.


## CLI torrent

A versão 3.10.0 inclui o comando `eazy-tor`, baseado em aria2c, para arquivos `.torrent` e links magnet. O destino padrão é `~/Downloads/Torrents`. Exemplos: `torrent arquivo.torrent`, `torrent --tor "magnet:?xt=urn:btih:..."` e `torrent -d /mnt/torrents --no-seed arquivo.torrent`. A opção `--tor` usa `torsocks` somente quando informada.


O torrent também faz parte do eazy: use `eazy --torrent --help` ou `eazy --torrent arquivo.torrent`. Ao adicionar um magnet ou `.torrent` pelo Ctrl+B, o eazy identifica o item e executa o módulo torrent na fila.


Arquitetura: o **eazy gerencia links e filas**; o downloader torrent fica separado no comando **`eazy-tor`**. O eazy chama `eazy-tor` somente quando a fila contém um magnet ou arquivo `.torrent`.


## Lotes de torrents e monitoramento

Use `eazy --torrent-list` para criar `~/.config/eazy/torrents.list` a partir dos torrents da fila. Edite o arquivo deixando um magnet ou `.torrent` por linha. Execute `eazy-tor --list ~/.config/eazy/torrents.list --log ~/.config/eazy/torrents.log`. O processamento é sequencial, continua após falhas e exibe resumo; use `--stop-on-error` quando necessário. O log persistente permite acompanhar o lote com `tail -f ~/.config/eazy/torrents.log`.
