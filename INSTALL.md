# Instalar o eazy 3.2

## Pacote .deb (Debian / Ubuntu / Mint / Pop!_OS)

### 1) Baixar o pacote

Na página do repositório ou de um **Release**:

- arquivo: `eazy_3.2_all.deb`

Ou, se estiver clonando o repo e o `.deb` estiver na raiz:

```bash
git clone https://github.com/vapesmadcat-blip/Easy_Player.git
cd Easy_Player
```

### 2) Instalar

```bash
sudo apt install ./eazy_3.2_all.deb
```

Alternativa:

```bash
sudo dpkg -i eazy_3.2_all.deb
sudo apt-get install -f
```

O `apt install ./arquivo.deb` resolve dependências automaticamente.

### 3) Usar

```bash
eazy --version
eazy --help
eazy
eazy ~/Vídeos
eazy -m
```

### Remover

```bash
sudo apt remove eazy
```

A pasta `~/.config/eazy/` **não** é apagada (config e filas). Para limpar tudo:

```bash
rm -rf ~/.config/eazy
```

---

## Sem .deb (script)

```bash
git clone https://github.com/vapesmadcat-blip/Easy_Player.git
cd Easy_Player
chmod +x install.sh eazy
./install.sh
```

---

## Dependências

**Obrigatórias:** `bash`, `fzf`, `whiptail`, `find`, `awk`  
**Recomendadas:** `mpv`, `wget`/`curl`, `ffmpeg`  
**Opcionais:** `yt-dlp`, `aria2`, `axel`, `chafa`, `p7zip-full`

O `.deb` declara as obrigatórias; o `apt` instala o que faltar.
