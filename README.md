# eazy 3.8.1 (release)

Navegador e reprodutor multimídia no **terminal** — fzf + mpv/mplayer/cvlc/ffplay.

**Repo:** https://github.com/vapesmadcat-blip/Easy_Player

## Destaques 3.3

- **Man page completa** no `.deb` e no `eazy --install`
- **Legenda de cores** na linha inferior (DIR / VID / AUD / IMG / ZIP / DOC)
- **Seleção global**: quantidade + bytes ao zerar; lista em F9
- **Extensões na pesquisa** no formato `INCLUIR MPG — CATEGORIA VIDEOS`
- **Links**: abrir no browser ou adicionar à fila (Ctrl+B); edição da fila
- **Exportar notas**, IA smithi (preferência), data/hora no status
- **Cache** de busca / listas / playlist
- **Limpeza** de caches (gradle, snap, …) na manutenção
- **Instalador** com detecção **GNOME** e **KDE** + deps do ambiente
- Pacote `.deb` compatível com GNOME e KDE Plasma

## IA integrada

O eazy inclui um chat opcional via API compatível com OpenRouter. Configure a chave
sem gravá-la no código:

```bash
export EAZY_AI_API_KEY="sua-chave"
eazy --ai
```

Também é possível criar `~/.config/eazy/ai.env` com permissão `600`:

```text
EAZY_AI_API_KEY=sua-chave
EAZY_AI_MODEL=gryphe/mythomax-l2-13b
```

O chat também pode ser aberto em **F9 → Abrir chat com IA**. A chave enviada ao
projeto não é incluída no código nem no pacote.

## Instalação rápida

```bash
sudo dpkg -i eazy_3.3.5_all.deb && sudo apt-get install -f
# GNOME: sudo apt install ./eazy-gnome_3.3.2_all.deb
# KDE Plasma: sudo apt install ./eazy-kde_3.3.2_all.deb
# ou
./eazy --install
```

Detalhes: [INSTALL.md](INSTALL.md) · Ajuda: `man eazy` · `eazy --help`

## Atalhos principais

| Tecla | Ação |
|-------|------|
| Enter | Tocar / entrar na pasta |
| Tab · Espaço | Marcar (persistente) |
| Ctrl+F | Busca recursiva |
| Ctrl+D | Duplicados |
| Ctrl+B | Downloads (editar / adicionar) |
| Ctrl+P | Filas / playlists |
| F9 | Configuração + overview |
| F10 | Ajuda |
| Alt+Enter | Executar seleção acumulada |
| Q | Sair |

## Cores na lista

| Cor | Tipo |
|-----|------|
| Azul | Diretório |
| Ciano | Vídeo |
| Amarelo | Áudio / playlist |
| Magenta | Imagem |
| Vermelho | Compactado |
| Verde | Documento / outros |

## Documentação

- `EAZY_EXPLICADO.md` — visão detalhada
- `GUIA_RAPIDO.md` — referência rápida
- `CHANGELOG.md` — histórico
- `man eazy` — manual instalado

## Licença

Uso livre. Sem garantias.

## Atualização 3.5.0

- **Enter em `.deb`**: exibe os metadados, pede confirmação e instala pelo APT.
- **Lista**: mostra `TAM · DATA · TIPO`; as cores seguem o ciclo visual `idx3`.
- **Ajuda**: `eazy --help` e `F10` incluem os atalhos e o fluxo de instalação.
- **Manual**: `man eazy` documenta todos esses recursos.


## Destino dos downloads

O destino padrão é **`~/Downloads`**. Para alterar, use **F9 → Configurar → Pasta Padrão de Downloads**. A escolha fica salva em `~/.config/eazy/config`. Também é possível iniciar com `DOWNLOAD_DIR=/caminho eazy`.


## Downloaders, Tor e parâmetros

Em **F9 → Downloads — downloader, Tor e parâmetros**, escolha aria2c, Axel, wget ou yt-dlp, ative opcionalmente Tor (`socks5://127.0.0.1:9050`) e informe parâmetros extras. O default para links diretos continua sendo **aria2c**; o Axel usa **`--insecure -n 4`** por padrão. A configuração fica em `~/.config/eazy/config`.


## Tor e torsocks

O instalador `eazy --install` inclui `tor` e `torsocks` quando o sistema oferece esses pacotes. Manualmente, use `sudo apt update && sudo apt install tor torsocks -y` (Debian/Ubuntu/Mint), `sudo dnf install tor torsocks -y` (Fedora/RHEL) ou `sudo pacman -S tor torsocks` (Arch). Inicie com `sudo systemctl start tor` e, se desejar, `sudo systemctl enable tor`.

Ao adicionar um link, marque **Usar Tor neste download**. O eazy usa SOCKS5 em `127.0.0.1:9050`. Para testar: `torsocks curl https://icanhazip.com`. Para aria2c, Axel e wget, o eazy usa `torsocks` automaticamente quando o checkbox está marcado. Teste separadamente com `torsocks curl https://icanhazip.com`.


## CLI torrent

A versão 3.9.1 inclui o comando `torrent`, baseado em aria2c, para arquivos `.torrent` e links magnet. O destino padrão é `~/Downloads/Torrents`. Exemplos: `torrent arquivo.torrent`, `torrent --tor "magnet:?xt=urn:btih:..."` e `torrent -d /mnt/torrents --no-seed arquivo.torrent`. A opção `--tor` usa `torsocks` somente quando informada.


O torrent também faz parte do eazy: use `eazy --torrent --help` ou `eazy --torrent arquivo.torrent`. Ao adicionar um magnet ou `.torrent` pelo Ctrl+B, o eazy identifica o item e executa o módulo torrent na fila.
