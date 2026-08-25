# Instalação do eazy

## Debian / Ubuntu — versão 3.0-11

A instalação oficial usa a **Release do GitHub**, o pacote `.deb` e seu checksum SHA-256:

```bash
curl -fLO https://github.com/vapesmadcat-blip/Easy_Player/releases/download/eazy-v3.0-11/eazy_3.0-11_all.deb
curl -fLO https://github.com/vapesmadcat-blip/Easy_Player/releases/download/eazy-v3.0-11/eazy_3.0-11_all.deb.sha256
sha256sum -c eazy_3.0-11_all.deb.sha256
sudo apt install ./eazy_3.0-11_all.deb
eazy
```

O comando `sha256sum -c` deve informar `OK` antes da instalação. Não instale o pacote se a verificação falhar.

Para remover os arquivos baixados depois da instalação:

```bash
rm -f eazy_3.0-11_all.deb eazy_3.0-11_all.deb.sha256
```

## Atualização a partir do código

```bash
git clone https://github.com/vapesmadcat-blip/Easy_Player.git
cd Easy_Player
chmod +x packaging/build-deb.sh
./packaging/build-deb.sh
sha256sum packaging/eazy/dist/eazy_3.0-11_all.deb
sudo apt install ./packaging/eazy/dist/eazy_3.0-11_all.deb
eazy
```

## Instalação rápida sem `.deb`

```bash
chmod +x eazy
./eazy --install
eazy
```

O instalador configura o comando em `/usr/local/bin/eazy` e o launcher `.desktop`. Para desinstalar essa instalação:

```bash
./eazy --uninstall
```

## Dependências

```bash
sudo apt update
sudo apt install -y fzf mpv mplayer gawk sed findutils whiptail wget \
  axel aria2 unzip p7zip-full rar yt-dlp lm-sensors
```

Recursos opcionais: `chafa`, `ffmpeg`, `vlc`, `smartmontools`, `pciutils`, `lshw`, `inxi`, `dmidecode`, `usbutils`, `mesa-utils` e `vulkan-tools`.

## Recursos da versão 3.0-11

A atualização inclui HELP EXPANDIDO no `F10`, saída com `Esc` da busca recursiva, barras de progresso na busca de duplicados e na limpeza/análise do HD, menu `Ctrl-K` completo, monitoramento de temperatura da CPU, autenticação sudo por caixa de senha e indicador persistente de DRY-RUN.

## Verificação

```bash
eazy --version
eazy --help
```

O arquivo de configuração e os dados da sessão ficam em `~/.config/eazy/` e não são removidos durante a atualização do pacote.
