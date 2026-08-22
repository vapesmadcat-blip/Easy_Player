# eazy 3.0 (professional)

Primeira publicação do pacote Debian do eazy, navegador e reprodutor multimídia no terminal.

O pacote `eazy_3.0-1_all.deb` instala:

- `/usr/bin/eazy`
- `/usr/share/applications/eazy.desktop`
- documentação em `/usr/share/doc/eazy/`

## Instalação

```bash
curl -fLO https://github.com/vapesmadcat-blip/Easy_Player/releases/download/eazy-v3.0/eazy_3.0-1_all.deb
sudo apt install ./eazy_3.0-1_all.deb
```

O pacote declara as dependências mínimas para executar o aplicativo. Os recursos opcionais de download, preview e formatos adicionais podem exigir `yt-dlp`, `aria2`, `axel`, `chafa`, `ffmpeg`, `p7zip-full` ou `rar`.

## Verificação

```bash
eazy --version
eazy --help
```

SHA-256 disponível no arquivo `eazy_3.0-1_all.deb.sha256` anexado à release.
