# eazy 3.13 — instalar e atualizar o repo

Zip em `~/prj`, repo em `~/prj/Easy_Player`.

## Dependências

Em Ubuntu ou Debian:

```bash
sudo apt update
sudo apt install -y bash fzf whiptail mpv ffmpeg curl wget python3 build-essential zlib1g-dev
```

## Reinstalar via `.deb` diretamente do repositório

Este procedimento reinstala o Eazy 3.13 completo, sem executar `uninstall` e sem apagar `~/.config/eazy`:

```bash
cd /tmp
curl -fL -o eazy_3.13_all.deb \
  https://raw.githubusercontent.com/vapesmadcat-blip/Easy_Player/main/eazy_3.13_all.deb
sudo apt install ./eazy_3.13_all.deb
eazy --version
```

O pacote instala o binário protegido, o editor de notas, a man page e o lançador compatível com KDE Plasma. Para atualizar o cache do KDE manualmente, use:

```bash
kbuildsycoca6 --noincremental 2>/dev/null || kbuildsycoca5 --noincremental 2>/dev/null || true
```

## Usar a versão-fonte

```bash
cd ~/prj
unzip -o eazy-3.2.10-release.zip
cp -f eazy-3.2.10-release/* ~/prj/Easy_Player/
cd ~/prj/Easy_Player
chmod +x eazy install.sh eazy-notes-editor 2>/dev/null || true
./eazy --install
eazy --version
```

## Usar o executável Linux

O executável pré-compilado está em `bin/eazy-linux-x86_64` e é destinado a Linux 64 bits x86_64/amd64:

```bash
cd ~/prj/Easy_Player
chmod +x bin/eazy-linux-x86_64
./bin/eazy-linux-x86_64
```

Para instalá-lo como comando do sistema:

```bash
sudo install -Dm755 bin/eazy-linux-x86_64 /usr/local/bin/eazy
eazy
```

## Recompilar o executável

O compilador está em `tools/compilar-eazy.sh`:

```bash
cd ~/prj/Easy_Player
chmod +x tools/compilar-eazy.sh
tools/compilar-eazy.sh eazy bin/eazy-linux-x86_64
```

O arquivo `eazy` original não é alterado. Depois da compilação, confira o checksum:

```bash
sha256sum bin/eazy-linux-x86_64
```

## Publicar alterações

```bash

git add eazy eazy-3.2.10 VERSION README.md CHANGELOG.md INSTALL.md \
        eazy.desktop install.sh eazy-notes-editor \
        eazy_3.2.10_all.deb eazy_3.2.10_all.deb.sha256 2>/dev/null || true
git add -A
git commit -m "Adiciona executável Linux e script de compilação"
git push origin main
```
