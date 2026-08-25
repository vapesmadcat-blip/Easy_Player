# Instalação do eazy

## Debian / Ubuntu — atualização 3.0-11

Baixe o pacote Debian da release e instale-o com `apt`:

```bash
wget https://github.com/vapesmadcat-blip/Easy_Player/raw/main/packaging/eazy/dist/eazy_3.0-11_all.deb
sudo apt install ./eazy_3.0-11_all.deb
```

Se o sistema indicar dependências pendentes, conclua com:

```bash
sudo apt -f install
```

Para remover o arquivo baixado depois da instalação:

```bash
rm -f eazy_3.0-11_all.deb
```

## Gerar e instalar localmente

```bash
git clone https://github.com/vapesmadcat-blip/Easy_Player.git
cd Easy_Player
chmod +x packaging/build-deb.sh
./packaging/build-deb.sh
sudo apt install ./packaging/eazy/dist/eazy_3.0-11_all.deb
```

## Instalação rápida sem `.deb`

```bash
chmod +x eazy
./eazy --install
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
