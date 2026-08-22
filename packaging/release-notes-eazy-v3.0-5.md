# eazy 3.0-5 (professional)

Esta versão amplia o **Overview do sistema** disponível dentro do menu **F9**.

O overview agora reúne, quando disponíveis, dados do sistema operacional, kernel, arquitetura, boot, ambiente gráfico, display server, locale, uptime, CPU, threads, frequência e governador, load average, RAM, swap, placa-mãe, BIOS, firmware, discos, SSDs, partições, montagens, uso dos filesystems, saúde SMART, USB, PCI, GPU, drivers, OpenGL, Vulkan, monitores, servidor de áudio, sinks, sources, ALSA, mixer, rede, Wi-Fi, DNS, rotas, bateria, energia, sensores térmicos, processos e versões das ferramentas usadas pelo eazy.

O coletor é tolerante à ausência de comandos opcionais: cada seção informa quando uma fonte de diagnóstico não está instalada ou não pode ser lida. O teste de som do F9 permanece disponível separadamente e continua pedindo confirmação antes de emitir o tom de teste.

Para habilitar a maior quantidade de dados, instale os utilitários recomendados:

```bash
sudo apt update
sudo apt install pciutils alsa-utils pulseaudio-utils lshw smartmontools dmidecode inxi usbutils x11-xserver-utils mesa-utils vulkan-tools iw network-manager upower lm-sensors
```

## Instalação ou atualização

```bash
curl -fLO https://github.com/vapesmadcat-blip/Easy_Player/releases/download/eazy-v3.0-5/eazy_3.0-5_all.deb
curl -fLO https://github.com/vapesmadcat-blip/Easy_Player/releases/download/eazy-v3.0-5/eazy_3.0-5_all.deb.sha256
sha256sum -c eazy_3.0-5_all.deb.sha256
sudo apt install ./eazy_3.0-5_all.deb
```
