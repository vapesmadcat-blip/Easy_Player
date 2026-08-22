# eazy 3.0-4 (professional)

Esta versão adiciona diagnóstico de hardware e teste de som diretamente ao menu **F9**.

A opção **Overview do sistema** apresenta a versão do sistema operacional, kernel, hostname, ambiente gráfico, shell, memória RAM, swap, discos, sistemas de arquivos, drives removíveis, servidor e dispositivos de áudio, GPU, driver de vídeo, monitores e módulos gráficos/áudio carregados. As informações que dependem de ferramentas opcionais são exibidas como indisponíveis quando o comando correspondente não está instalado.

A opção **Teste de som** pede confirmação antes de emitir um tom de 440 Hz. Ela usa o primeiro método disponível entre `speaker-test`, `ffplay`, `paplay` e `canberra-gtk-play`, informando o resultado ao terminar.

## Instalação ou atualização

```bash
curl -fLO https://github.com/vapesmadcat-blip/Easy_Player/releases/download/eazy-v3.0-4/eazy_3.0-4_all.deb
curl -fLO https://github.com/vapesmadcat-blip/Easy_Player/releases/download/eazy-v3.0-4/eazy_3.0-4_all.deb.sha256
sha256sum -c eazy_3.0-4_all.deb.sha256
sudo apt install ./eazy_3.0-4_all.deb
```

Ferramentas opcionais recomendadas para ampliar o diagnóstico e o teste de som:

```bash
sudo apt install pciutils alsa-utils pulseaudio-utils
```
