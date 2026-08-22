# eazy 3.0-6 (professional)

Esta versão adiciona uma seleção automática no modo **Duplicados**.

Ao pressionar **F11**, o eazy seleciona um arquivo existente de cada grupo de duplicatas. O primeiro caminho de cada grupo, em ordem determinística, é usado como representante. A quantidade de grupos selecionados aparece no cabeçalho e a seleção fica disponível para Enter, Insert, apagar, copiar ou mover.

A seleção manual não foi alterada: **Tab**, Espaço, Ctrl-A, Ctrl-X e Ctrl-R continuam funcionando normalmente. Se o usuário alterar a seleção manualmente depois de usar F11, a seleção manual passa a ter prioridade.

## Instalação ou atualização

```bash
curl -fLO https://github.com/vapesmadcat-blip/Easy_Player/releases/download/eazy-v3.0-6/eazy_3.0-6_all.deb
curl -fLO https://github.com/vapesmadcat-blip/Easy_Player/releases/download/eazy-v3.0-6/eazy_3.0-6_all.deb.sha256
sha256sum -c eazy_3.0-6_all.deb.sha256
sudo apt install ./eazy_3.0-6_all.deb
```
