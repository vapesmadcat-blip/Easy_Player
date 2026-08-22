# eazy 3.0-8 (professional)

Esta versão melhora a seleção no modo **Duplicados**.

Ao usar **F12**, cada arquivo escolhido automaticamente passa a aparecer com a marca visual **✓** na lista. O cabeçalho mostra a quantidade de itens selecionados e o total de bytes, por exemplo: `Sel: 12.4M (3 item(ns))`.

O **Ctrl-R** agora marca todos os duplicados corretamente e atualiza o mesmo contador e o total de bytes. Tab, Espaço, Ctrl-A e Ctrl-X continuam disponíveis para a seleção manual. Se a seleção manual for alterada depois do F12, ela passa a ter prioridade.

## Instalação ou atualização

```bash
curl -fLO https://github.com/vapesmadcat-blip/Easy_Player/releases/download/eazy-v3.0-8/eazy_3.0-8_all.deb
curl -fLO https://github.com/vapesmadcat-blip/Easy_Player/releases/download/eazy-v3.0-8/eazy_3.0-8_all.deb.sha256
sha256sum -c eazy_3.0-8_all.deb.sha256
sudo apt install ./eazy_3.0-8_all.deb
```
