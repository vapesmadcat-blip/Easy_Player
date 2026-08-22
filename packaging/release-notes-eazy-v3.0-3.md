# eazy 3.0-3 (professional)

Esta versão corrige a navegação e a persistência de posição do eazy.

Ao pressionar **Ctrl+Backspace**, o eazy alterna para o último diretório visitado, preservando a posição do cursor em ambos os diretórios. Em versões antigas do `fzf` que não diferenciam Ctrl+Backspace, **Ctrl+H** funciona como compatibilidade.

A posição agora é sincronizada pelo índice real do cursor no `fzf`, incluindo **Page Down**, **Page Up**, Home, End e movimentos feitos com as setas. As filas temporárias, o histórico e os arquivos `.m3u` mantêm posições independentes.

## Instalação ou atualização

```bash
curl -fLO https://github.com/vapesmadcat-blip/Easy_Player/releases/download/eazy-v3.0-3/eazy_3.0-3_all.deb
curl -fLO https://github.com/vapesmadcat-blip/Easy_Player/releases/download/eazy-v3.0-3/eazy_3.0-3_all.deb.sha256
sha256sum -c eazy_3.0-3_all.deb.sha256
sudo apt install ./eazy_3.0-3_all.deb
```

Depois de instalar, feche e abra o eazy novamente para carregar a nova versão.
