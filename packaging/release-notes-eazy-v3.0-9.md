# eazy 3.0-9 (professional)

Esta versão reestrutura a seleção no modo **Duplicados** para que as marcações não sejam perdidas quando a lista é redesenhada.

A seleção agora fica em uma lista temporária dedicada, validada contra os caminhos duplicados existentes. Cada ação de seleção atualiza essa mesma fonte de verdade, e as linhas selecionadas continuam marcadas visualmente com **✓**. O cabeçalho mantém a contagem e o total de bytes selecionados após F12, Tab, Espaço, Ctrl-A, Ctrl-X e Ctrl-R.

O **Ctrl-R** passa a inverter de fato a seleção atual: os arquivos selecionados são removidos e todos os demais caminhos duplicados existentes são incluídos. Assim, após **F12**, Ctrl-R seleciona os demais representantes de cada grupo; após **Ctrl-A**, Ctrl-R limpa a seleção; e com a seleção vazia, Ctrl-R seleciona todos os duplicados.

O **F12** continua selecionando um arquivo existente por grupo. **Tab/Espaço** alternam o item focado, **Ctrl-A** seleciona todos e **Ctrl-X** limpa todos. Enter, Insert, apagar, copiar, mover e embaralhar consomem a seleção persistente, em vez de depender apenas do retorno transitório do fzf.

## Instalação ou atualização

```bash
curl -fLO https://github.com/vapesmadcat-blip/Easy_Player/releases/download/eazy-v3.0-9/eazy_3.0-9_all.deb
curl -fLO https://github.com/vapesmadcat-blip/Easy_Player/releases/download/eazy-v3.0-9/eazy_3.0-9_all.deb.sha256
sha256sum -c eazy_3.0-9_all.deb.sha256
sudo apt install ./eazy_3.0-9_all.deb
```
