# eazy 3.0-2 (professional)

Correção do pacote Debian do eazy 3.0: ao selecionar um arquivo `.m3u` e pressionar **Enter**, a playlist agora é aberta no navegador interno do eazy, sem iniciar o player imediatamente.

A reprodução continua disponível ao selecionar os itens dentro da playlist. As ações existentes para tocar playlists também permanecem disponíveis.

O pacote `eazy_3.0-2_all.deb` instala:

- `/usr/bin/eazy`
- `/usr/share/applications/eazy.desktop`
- documentação em `/usr/share/doc/eazy/`

## Instalação

```bash
curl -fLO https://github.com/vapesmadcat-blip/Easy_Player/releases/download/eazy-v3.0-2/eazy_3.0-2_all.deb
curl -fLO https://github.com/vapesmadcat-blip/Easy_Player/releases/download/eazy-v3.0-2/eazy_3.0-2_all.deb.sha256
sha256sum -c eazy_3.0-2_all.deb.sha256
sudo apt install ./eazy_3.0-2_all.deb
```

## Verificação

```bash
eazy --version
eazy --help
```
