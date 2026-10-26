# Easy Player 5.0.0

Navegador e reprodutor multimídia no terminal, com seleção persistente, playlists, downloads, manutenção, IA, editor de notas, torrents e uma Central completa de streaming.

## Instalação

```bash
curl -fsSL https://raw.githubusercontent.com/vapesmadcat-blip/Easy_Player/main/install-from-web.sh | bash
```

Para instalar o pacote manualmente:

```bash
curl -fLO https://github.com/vapesmadcat-blip/Easy_Player/releases/download/v5.0.0/eazy_5.0.0_all.deb
curl -fLO https://github.com/vapesmadcat-blip/Easy_Player/releases/download/v5.0.0/eazy_5.0.0_all.deb.sha256
sha256sum -c eazy_5.0.0_all.deb.sha256
sudo apt install ./eazy_5.0.0_all.deb
```

## Streaming

A Central é aberta com `eazy --stream` ou pelo menu de streams do `Ctrl-B`. Ela usa `yt-dlp`, mostra a duração dos vídeos, mantém histórico de pesquisas e filmes assistidos, pergunta ao terminar se o filme deve ir para os favoritos e permite carregar mais 30 resultados sem repetir a consulta. Também inclui canais públicos de filmes, TV aberta, download, áudio e abertura no navegador.

Na tela `Filmes gratuitos`, a opção `Histórico — filmes selecionados com Enter` reabre os títulos escolhidos anteriormente. Os dados ficam em `~/.config/eazy/yt-stream/`, incluindo `searches.tsv`, `watch_history.tsv` e `favorites.tsv`. O pacote instala o componente em `/usr/bin/eazy-yt-stream` e `/usr/lib/eazy/eazy-yt-stream`.

## Componentes

A release inclui `eazy`, `eazy-yt-stream`, `eazy-tor`, `eazy-ai.py`, `eazy-notes-editor`, launcher desktop, man page e help HTML/TXT. O instalador não usa caminhos de usuário fixos e não instala arquivos na raiz do projeto.

## Desenvolvimento

```bash
bash -n eazy eazy-yt-stream
./packaging/build-deb.sh
./eazy --version
./eazy --help
```

Para recompilar o binário Linux, use `./tools/compilar-eazy.sh eazy bin/eazy-linux-x86_64`. O executável compilado continua dependendo das ferramentas do sistema usadas pelo Easy.

## Autoria

**Made by John B Kersting.**
