# eazy 3.2.4 (release)

**Autor:** João Kersting  
**Repositório:** [https://github.com/vapesmadcat-blip/Easy_Player](https://github.com/vapesmadcat-blip/Easy_Player)

**Navegador e reprodutor multimídia no terminal** — `fzf` + `mpv` (ou mplayer/cvlc/ffplay).

Seleção persistente entre pastas, filas temporárias, playlists, busca, duplicados, downloads e manutenção do sistema.

## Release Notes

**eazy-v3.2.4**

- **Enter** em `.html` / `.htm` / URL abre o **browser** (`xdg-open`, `gio`, Firefox, Chromium…)
- Caminho absoluto + `file://`; proteção em `tocar_arquivo` para não ir ao mpv
- Cabeçalho com **Revisão 3.2.4**
- Del = cursor; Shift+Del = seleção (amarelo nos duplicados)
- F9 → Lixeira, Exportar notas
- Prune da seleção global após delete
- Filtros com extensões no prompt



## Requisitos

**Obrigatórios**

- `bash`, `fzf`, `whiptail`, `find`, `awk`
- Um player: `mpv` (recomendado), `mplayer`, `cvlc` ou `ffplay`

**Opcionais**

- `yt-dlp`, `aria2c`, `axel`, `wget` — downloads  
- `ffmpeg`, `chafa`, `imagemagick`, `poppler-utils`, `img2pdf` — preview e conversões  
- `p7zip`, `unzip` — arquivos compactados  
- `xdg-utils` — abrir HTML e links no browser  
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
sudo apt install ./eazy_3.2.3_all.deb
# ou:
sudo dpkg -i eazy_3.2.3_all.deb
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
eazy --restore-keys
```

## Seleção (3.2.3)

| Tecla | Comportamento |
|--------|----------------|
| **Tab / Espaço** | Marca o item — a seleção **persiste** entre pastas |
| **Enter** | Executa **só** o item sob o cursor (HTML/URL → browser) |
| **Ctrl+Espaço / F6** | Seleção inteira (recomendado; Alt+Enter depende do terminal) |
| **Ctrl-A / Ctrl-X / Ctrl-R** | Todos visíveis / limpar pasta atual / inverter |
| **Del** | Apaga **só o arquivo sob o cursor** |
| **Shift+Del** | Seleção: pergunta **local** ou **global** (duplicados: seleção amarela) |
| **Alt-D** | Apagar do disco (seleção de ações) |
| **F12** | Reaplica a persistência como multi-select do fzf |
| **Insert** | Envia a seleção para fila tmp 1/2/3 ou lista personalizada |
| **Ctrl-K / Y / U / E** | Ações, copiar, mover, shuffle |

Arquivo de persistência: `~/.config/eazy/selected_paths` (atualizado automaticamente quando há delete)

## Atalhos principais

| Tecla | Função |
|--------|--------|
| Ctrl-F | Busca recursiva |
| Ctrl-D | Duplicados |
| Ctrl-P | Alternar filas / listas / diretório |
| Ctrl-O | Abrir playlist `.m3u` / `.pls` |
| Ctrl-G | Histórico |
| Ctrl-B | Downloads |
| Ctrl-N | Notas rápidas |
| Ctrl-L | Ir à pasta do arquivo |
| Ctrl-/ | Preview on/off |
| F4–F7 | Filtros (audios / videos / imgs / compactados) com extensões no prompt |
| F9 | Config, Hotkeys, overview, som, **lixeira**, **exportar notas** |
| F10 | Ajuda expandida |
| Q / X / Ctrl-Q | Sair (salva sessão) |

## Editor de Notas

| Tecla | Ação |
|--------|--------|
| `Ctrl-N` | Nova nota |
| `Ctrl-S` | Salva e abre outra nota |
| `Esc` | Salva e sai |
| `Enter` | Nova linha (com quebra automática) |
| `Backspace` | Apaga |
| `Ctrl-E` | Lista compacta de notas |
| `Del` | Apaga a nota selecionada |
| `Ctrl-R` | Renomeia a nota selecionada |
| `Ctrl-I` | Importar notas de arquivo externo |
| `Ctrl-X` | Exporta para `~/Documentos/Easy-Notes/` |

Também: **F9 → Exportar notas** no navegador principal.

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
| `keys` | Atalhos personalizados (F9 → Hotkeys) |
| `session` | Sessão ao sair |
| `selected_paths` | Seleção persistente |
| `temp_playlist_1..3` | Filas temporárias |
| `history` | Histórico |
| `notas/` | Notas rápidas |
| `scripts/manut-completa.sh` | Manutenção completa |

## Licença

Uso livre. Sem garantias.

---

**eazy 3.2.4 · release**  
Desenvolvido por João Kersting