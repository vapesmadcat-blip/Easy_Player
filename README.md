# eazy 3.0 (professional)

Navegador e reprodutor multimídia no **terminal** — rápido, com teclado e poucas dependências.

Constrói sobre **fzf** + **mpv** (ou mplayer / VLC CLI / ffplay).

## Instalação

### Rápida (qualquer distro)

```bash
chmod +x eazy.sh
./eazy.sh --install      # deps + /usr/local/bin/eazy + .desktop
./eazy.sh --uninstall    # remove comando e launcher
```

Detecta: **apt**, **pacman**, **dnf**, **zypper**, **apk**.

### Debian / Ubuntu (.deb)

```bash
chmod +x packaging/build-deb.sh && ./packaging/build-deb.sh
sudo dpkg -i packaging/eazy_3.0-1_all.deb
sudo apt-get install -f
```

### Arch / Manjaro

```bash
./packaging/build-arch.sh
cd packaging/arch/build && makepkg -si
```

### Fedora / RHEL

```bash
rpmbuild -ba packaging/rpm/eazy.spec   # com sources configuradas
```

### Dependências manuais (apt)

```bash
sudo apt update && sudo apt install -y \
  fzf mpv mplayer gawk sed findutils whiptail wget \
  axel aria2 unzip p7zip-full rar yt-dlp
```

Opcionais: `chafa`, `ffmpeg`, `vlc`.

## Uso

```bash
eazy                  # última sessão ou pasta padrão
eazy ~/Videos         # abre nesta pasta
eazy ./filme.mp4      # pasta do arquivo + cursor no arquivo
eazy --help
eazy --version
eazy --config
```

## Atalhos

| Tecla | Ação |
|-------|------|
| `Enter` | Tocar / entrar na pasta |
| `Tab` / `Espaço` | Marcar |
| `Insert` | Enviar para fila 1, 2 ou 3 |
| `Ctrl-P` | Alternar filas 1→2→3→diretório |
| `Ctrl-F` | Busca recursiva |
| `Ctrl-D` | Duplicados |
| `Ctrl-B` | Downloads |
| `Ctrl-K` | Menu de ações |
| `Ctrl-L` | Ir à pasta do arquivo |
| `Ctrl-/` | Preview on/off |
| `Del` | Remover (lista ou disco, conforme contexto) |
| `Alt-D` | Apagar do disco (em playlist/fila) |
| `F9` | Configuração |
| `Q` | Sair |

### No mpv

| Tecla | Ação |
|-------|------|
| `d` | Marcar para exclusão ao sair |
| `D` | Marcar e próximo da playlist |

## Configuração

Tudo em `~/.config/eazy/`:

- `config` — player, volume, pastas, preview, sem áudio  
- `session` — última pasta e estado  
- `temp_playlist_1..3` — filas temporárias  
- `history` — últimos tocados  
- `marked_delete` — marcados no mpv  

## Características

- 3 filas temporárias persistentes  
- Busca com progresso, cache em sessão, filtro de tamanho e conteúdo  
- Preview de imagens (chafa) e metadados de mídia  
- Sessão: pasta, cursor, filtro digitado, preview  
- Players: mpv, mplayer, cvlc, ffplay  

## Licença

Uso livre. Sem garantias.
