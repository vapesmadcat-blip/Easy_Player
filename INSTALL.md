# eazy 3.2.12 — Instalação

## Opção A — pacote `.deb` (Debian / Ubuntu / KDE / GNOME)

```bash
sudo dpkg -i eazy_3.2.12_all.deb
sudo apt-get install -f
eazy --version
man eazy
```

O pacote instala:

- `/usr/bin/eazy` e `/usr/lib/eazy/eazy`
- `/usr/lib/eazy/eazy-notes-editor`
- `/usr/share/applications/eazy.desktop` (menu GNOME e KDE)
- `/usr/share/man/man1/eazy.1.gz`
- documentação em `/usr/share/doc/eazy/`

## Opção B — a partir do repositório (`eazy --install`)

```bash
cd ~/prj/Easy_Player   # ou pasta do clone
chmod +x eazy install.sh eazy-notes-editor
./eazy --install
```

O instalador:

1. Detecta o gerenciador de pacotes (`apt`, `pacman`, `dnf`, `zypper`, `apk`)
2. Detecta o desktop (**GNOME** ou **KDE**)
3. Instala dependências principais + opcionais do ambiente
4. Copia o binário, o editor de notas, a man page e o launcher
5. Atualiza o menu do GNOME (`update-desktop-database`) e do KDE (`kbuildsycoca`)

### Dependências principais

`fzf` · `mpv` (ou mplayer/vlc) · `whiptail` · `gawk` · `findutils` · `sed` · `wget`/`curl` · `ffmpeg` · `xdg-utils`

### Opcionais úteis

`yt-dlp` · `aria2` · `axel` · `chafa` · `imagemagick` · `poppler-utils` · `p7zip-full`

### Extras por desktop

| Ambiente | Pacotes sugeridos |
|----------|-------------------|
| **KDE** | konsole, dolphin, kate, kio-extras |
| **GNOME** | gnome-terminal, nautilus, gedit, evince |

## Desinstalação

```bash
eazy --uninstall
# ou, se instalou via deb:
sudo apt remove eazy
```

## Atualizar o repositório (push)

```bash
cd ~/prj
unzip -o eazy-3.2.12-release.zip
cp -f eazy-3.2.12-release/* ~/prj/Easy_Player/
cp -rf eazy-3.2.12-release/packaging ~/prj/Easy_Player/ 2>/dev/null || true
cd ~/prj/Easy_Player
chmod +x eazy install.sh eazy-notes-editor 2>/dev/null || true
./eazy --install
eazy --version

git add -A
git commit -m "eazy 3.2.12: deb GNOME/KDE, man, legenda cores, deps --install"
git push origin main
```
