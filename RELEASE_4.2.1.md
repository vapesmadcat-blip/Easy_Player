# eazy 4.2.1

## Destaques
- **F10 help**: HTML completo no navegador, less no terminal, ou por seção
- Help HTML com IA, eazy-tor, torrents, Tor, Alt+0, filas, duplicados, manutenção
- Enter na fila de downloads: escolhe app (sugere o último)
- Alt+0: log real do terminal
- selected_paths auto-criado; tmp em `~/.config/eazy/tmp`

## Instalar (após publicar a release)

```bash
curl -fsSL https://raw.githubusercontent.com/vapesmadcat-blip/Easy_Player/main/install-from-web.sh | bash
```

```bash
VER=4.2.1
curl -fsSL -o eazy_${VER}_all.deb \
  "https://github.com/vapesmadcat-blip/Easy_Player/releases/download/eazy-v${VER}/eazy_${VER}_all.deb"
sudo dpkg -i eazy_${VER}_all.deb
```
