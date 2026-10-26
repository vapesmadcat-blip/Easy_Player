# Easy 5.0.0

A versão 5.0.0 usa o arquivo `easiea` enviado como base, preservando as melhorias de seleção, exportação, manutenção, diagnóstico e help. A Central de streaming revisada foi anexada como o componente `eazy-yt-stream`.

## Central de streaming

A Central pode ser aberta pelo menu de streams do Easy ou diretamente com:

```bash
eazy --stream
```

Ela oferece pesquisa com duração visível, 30 resultados por página, opção para mostrar mais 30, pesquisas salvas, favoritos, download, áudio, navegador, canais públicos de filmes e TV aberta. Os dados ficam em `~/.config/eazy/yt-stream/`.

## Componentes instalados

A instalação inclui `eazy`, `eazy-yt-stream`, `eazy-tor`, `eazy-ai.py`, `eazy-notes-editor`, launcher desktop, man page e documentação. Os binários do pacote ficam em `/usr/bin` e `/usr/lib/eazy`; não há caminho de usuário fixo como `/home/jim` no pacote.

## Verificações feitas

Foram validados a sintaxe Bash do Easy e do stream, a versão CLI, a integração do menu, a presença do stream no instalador e no pacote, os caminhos do instalador, os arquivos de IA/editor/Tor, o `update-all`, a man page e o conteúdo do pacote Debian. O pacote não instala artefatos na raiz do projeto nem usa `/home/jim`.

## Instalação rápida

```bash
curl -fLO https://github.com/vapesmadcat-blip/Easy_Player/releases/download/v5.0.0/eazy_5.0.0_all.deb
curl -fLO https://github.com/vapesmadcat-blip/Easy_Player/releases/download/v5.0.0/eazy_5.0.0_all.deb.sha256
sha256sum -c eazy_5.0.0_all.deb.sha256
sudo apt install ./eazy_5.0.0_all.deb
```

Ou:

```bash
curl -fsSL https://raw.githubusercontent.com/vapesmadcat-blip/Easy_Player/main/install-from-web.sh | bash
```

- O Help HTML e os arquivos HTML voltam a perguntar qual navegador usar, com suporte a Brave, Chrome, Edge, Firefox e padrão do sistema.
