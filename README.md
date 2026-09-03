# eazy 3.2 (release)

**Repositório:** [https://github.com/vapesmadcat-blip/Easy_Player](https://github.com/vapesmadcat-blip/Easy_Player)

**Navegador e reprodutor multimídia no terminal** — `fzf` + `mpv` (ou mplayer/cvlc/ffplay).

Seleção persistente entre pastas, filas temporárias, playlists, busca, duplicados, downloads e manutenção do sistema.

## Release Notes

**eazy-v3.2** — [Release Page](https://github.com/vapesmadcat-blip/Easy_Player/releases/tag/eazy-v3.2)

- Quebra de linha automática no editor
- Melhorias gerais de estabilidade

## Requisitos

**Obrigatórios**

- `bash`, `fzf`, `whiptail`, `find`, `awk`
- Um player: `mpv` (recomendado), `mplayer`, `cvlc` ou `ffplay`

**Opcionais**

- `yt-dlp`, `aria2c`, `axel`, `wget` — downloads  
- `ffmpeg`, `chafa`, `imagemagick`, `poppler-utils`, `img2pdf` — preview e conversões  
- `p7zip`, `unzip` — arquivos compactados  
- `smartmontools`, `lm-sensors` — diagnóstico  

## Instalação

### Direto do GitHub

```bash
git clone https://github.com/vapesmadcat-blip/Easy_Player.git
cd Easy_Player
chmod +x eazy install.sh
./install.sh
```

Ou em uma linha:

```bash
git clone https://github.com/vapesmadcat-blip/Easy_Player.git && cd Easy_Player && chmod +x eazy install.sh && ./install.sh
```

### Pacote .deb (Debian / Ubuntu / Mint)

```bash
sudo apt install ./eazy_3.2_all.deb
# ou:
sudo dpkg -i eazy_3.2_all.deb
sudo apt-get install -f
```

### Tarball

```bash
tar -xzf eazy-3.2.tar.gz
cd eazy-3.2
./install.sh
```

### Makefile

```bash
sudo make install
make install-full
```

### Arch Linux (PKGBUILD)

```bash
makepkg -si
```

### Remover

```bash
./uninstall.sh
# ou:
eazy --uninstall
sudo apt remove eazy
```

O instalador detecta o gerenciador de pacotes, instala dependências, copia para `/usr/local/bin/eazy`, cria `~/.config/eazy/` e o script de manutenção completa.

```bash
eazy --version
eazy --help
eazy -m
```

## Uso rápido

```bash
eazy
eazy ~/Vídeos
eazy arquivo.mp4
eazy --config
eazy -m
eazy --update-ytdlp
```

## Seleção (3.2)

| Tecla | Comportamento |
|--------|----------------|
| **Tab / Espaço** | Marca o item — a seleção **persiste** entre pastas |
| **Enter** | Executa **só** o item sob o cursor |
| **Alt+Enter** | Executa a **seleção inteira** (persistente + marcas do fzf) |
| **Ctrl-A / Ctrl-X / Ctrl-R** | Todos / limpar pasta atual / inverter (marcas + persistência) |
| **F12** | Reaplica a persistência como multi-select do fzf |
| **Insert** | Envia a seleção para fila tmp 1/2/3 ou lista personalizada |
| **Ctrl-K / Y / U / E** | Ações, copiar, mover, shuffle — mesma seleção do Alt+Enter |

Arquivo de persistência: `~/.config/eazy/selected_paths`

## Atalhos principais

| Tecla | Função |
|--------|--------|
| Ctrl-F | Busca recursiva |
| Ctrl-D | Duplicados |
| Ctrl-P | Alternar filas / listas / diretório |
| Ctrl-O | Abrir playlist `.m3u` / `.pls` |
| Ctrl-G | Histórico |
| Ctrl-B | Downloads |
| Ctrl-L | Ir à pasta do arquivo |
| Ctrl-/ | Preview on/off |
| Del / Alt-D | Remover da lista ou apagar do disco |
| F9 | Configuração / overview / som |
| F10 | Ajuda expandida |
| Q / X / Ctrl-Q | Sair (salva sessão) |

## Manutenção (`eazy -m`)

1. **Dados do próprio eazy** (sem sudo)
2. **Manutenção do sistema** (sudo quando necessário)
3. **Manutenção COMPLETA (sudo)** — RAM, disco, CPU, órfãos, TRIM, kernel, rede

```bash
eazy -m
eazy --maintenance
eazy -a
```

## Configuração

Arquivos em `~/.config/eazy/`:

| Arquivo | Uso |
|---------|-----|
| `config` | Player, volume, pastas, preview |
| `session` | Sessão ao sair |
| `selected_paths` | Seleção persistente |
| `temp_playlist_1..3` | Filas temporárias |
| `history` | Histórico |
| `scripts/manut-completa.sh` | Manutenção completa |

## Licença

Uso livre. Sem garantias.

---

**eazy 3.2 · release**
