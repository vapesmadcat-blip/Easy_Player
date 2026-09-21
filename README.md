# eazy 3.2.10 (release)

https://github.com/vapesmadcat-blip/Easy_Player

## Executável Linux

O binário protegido para Linux 64 bits fica em [`bin/eazy-linux-x86_64`](bin/eazy-linux-x86_64). Para usar:

```bash
cd bin
chmod +x eazy-linux-x86_64
./eazy-linux-x86_64
```

O binário foi compilado para arquiteturas **x86_64/amd64** e ainda requer as dependências usadas pelo Eazy, como `bash`, `fzf`, `whiptail`, `mpv`, `ffmpeg`, `curl` e `wget`.

Para recompilar o binário a partir do código-fonte atual:

```bash
./tools/compilar-eazy.sh eazy bin/eazy-linux-x86_64
```

O script de compilação gera um wrapper executável para scripts Bash grandes e não modifica o arquivo-fonte original.

## Destaques
- Enter em `.py` / `.sh` / `.html`: menu estilo PDF (Executar | Ver | Editar | Voltar)
- PYTHON_CMD / SHELL_CMD no F9
- Alt-X com quantidade e bytes
- F9 shell + EXIT_DIR_MODE + --shell-init
- HTML no browser, Del/Shift+Del, lixeira

## Instalação
Consulte [INSTALL.md](INSTALL.md) para instalação pela fonte, uso do binário e recompilação.

## Autoria

**Made by John B Kersting.**

Para reinstalar completamente a versão 3.13 diretamente deste repositório, sem desinstalar e preservando `~/.config/eazy`:

```bash
chmod +x reinstalar-eazy-3.13.sh
./reinstalar-eazy-3.13.sh
```

Também é possível reinstalar diretamente pelo pacote Debian publicado no repositório:

```bash
cd /tmp
curl -fL -o eazy_3.13_all.deb \
  https://raw.githubusercontent.com/vapesmadcat-blip/Easy_Player/main/eazy_3.13_all.deb
sudo apt install ./eazy_3.13_all.deb
```
