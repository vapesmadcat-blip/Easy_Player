# eazy — pacote Debian

Este diretório contém o empacotamento Debian do **eazy 3.0 (professional)**, um navegador e reprodutor multimídia no terminal.

## Instalação pelo GitHub Release

Depois que a release `eazy-v3.0-4` estiver publicada, em Debian ou Ubuntu execute:

```bash
curl -fLO https://github.com/vapesmadcat-blip/Easy_Player/releases/download/eazy-v3.0-4/eazy_3.0-4_all.deb
sudo apt install ./eazy_3.0-4_all.deb
```

O `apt` instala automaticamente as dependências declaradas pelo pacote. O comando fica disponível como `eazy`, e o launcher gráfico é instalado em `/usr/share/applications/eazy.desktop`. Ao selecionar um arquivo `.m3u` e pressionar Enter, o eazy abre a playlist no navegador interno. O menu F9 também oferece um overview do sistema (OS, RAM, discos, drives, áudio e vídeo) e um teste de som.

Para testar:

```bash
eazy --version
eazy --help
eazy ~/Videos
```

Para remover o programa, preservando a configuração do usuário:

```bash
sudo apt remove eazy
```

Os dados de sessão e configuração ficam em `~/.config/eazy/`.

## Dependências opcionais

Para habilitar downloads, previews e formatos adicionais, podem ser instalados `yt-dlp`, `aria2`, `axel`, `chafa`, `ffmpeg`, `p7zip-full` e `rar`. O pacote exige apenas o conjunto mínimo para iniciar o navegador e tocar mídia.

## Construção local

A partir da raiz deste repositório:

```bash
chmod +x packaging/build-deb.sh packaging/eazy/build-deb.sh
./packaging/build-deb.sh
```

O resultado será gerado em `packaging/eazy/dist/eazy_3.0-4_all.deb`. Para inspecionar o pacote sem instalá-lo:

```bash
dpkg-deb --info packaging/eazy/dist/eazy_3.0-4_all.deb
dpkg-deb --contents packaging/eazy/dist/eazy_3.0-4_all.deb
```

## Origem dos arquivos

O pacote usa os arquivos fornecidos para esta publicação: `eazy`, `eazy.desktop`, `README.md` e `CHANGELOG.md`. O binário instalado é `/usr/bin/eazy`; os documentos ficam em `/usr/share/doc/eazy/`.
