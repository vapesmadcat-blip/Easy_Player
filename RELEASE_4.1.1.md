# eazy 4.1.1

## Destaques
- Enter na fila de downloads: escolhe o app (aria/axel/wget/ytdlp/tor), sugere o último
- Alt+0: log real do terminal (por trás do fzf)
- selected_paths: cria pasta/arquivo automaticamente (sem spam de erro)
- Temporários em `~/.config/eazy/tmp` (não usa `/tmp` do sistema)
- HTML: tamanho de pastas ao lado do tipo
- Pacote KDE: eazy + eazy-tor + eazy-ai.py + eazy-notes-editor

## Instalar

```bash
curl -fsSL https://raw.githubusercontent.com/vapesmadcat-blip/Easy_Player/main/install-from-web.sh | bash
```

Ou:

```bash
VER=4.1.1
curl -fsSL -o eazy_${VER}_all.deb \
  "https://github.com/vapesmadcat-blip/Easy_Player/releases/download/v${VER}/eazy_${VER}_all.deb"
sudo dpkg -i eazy_${VER}_all.deb
```
