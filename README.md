# eazy 3.0 (professional)

Navegador e reprodutor multimídia no **terminal**, rápido, orientado por teclado e com poucas dependências. O projeto usa **fzf** em conjunto com **mpv**, mplayer, VLC CLI ou ffplay.

## Instalação

### Debian / Ubuntu: pacote `.deb` da Release

```bash
curl -fLO https://github.com/vapesmadcat-blip/Easy_Player/releases/download/eazy-v3.0-15/eazy_3.0-15_all.deb
curl -fLO https://github.com/vapesmadcat-blip/Easy_Player/releases/download/eazy-v3.0-15/eazy_3.0-15_all.deb.sha256
sha256sum -c eazy_3.0-15_all.deb.sha256
sudo apt install ./eazy_3.0-15_all.deb
eazy
```

Para corrigir dependências caso necessário:

```bash
sudo apt -f install
```

### Instalação rápida a partir do código

```bash
chmod +x eazy
./eazy --install
./eazy --uninstall
```

O instalador detecta apt, pacman, dnf, zypper e apk. As operações que exigem privilégios solicitam a senha em uma caixa segura antes da execução.

### Gerar o pacote Debian localmente

```bash
chmod +x packaging/build-deb.sh
./packaging/build-deb.sh
sudo apt install ./packaging/eazy/dist/eazy_3.0-15_all.deb
```

### Dependências manuais no Debian/Ubuntu

```bash
sudo apt update && sudo apt install -y \
  fzf mpv mplayer gawk sed findutils whiptail wget \
  axel aria2 unzip p7zip-full rar yt-dlp lm-sensors poppler-utils img2pdf
```

Opcionais: `chafa`, `ffmpeg`, `vlc`, `smartmontools`, `pciutils`, `lshw`, `inxi`, `dmidecode`, `usbutils`, `mesa-utils` e `vulkan-tools`.

## Uso

```bash
eazy
eazy ~/Videos
eazy ./filme.mp4
eazy --help
eazy --version
eazy --config
```

## Atalhos

| Tecla | Ação |
|---|---|
| `Enter` | Tocar, entrar na pasta ou abrir playlist `.m3u` |
| `Esc` | Sair da busca recursiva e voltar à pasta normal |
| `Ctrl-Backspace` | Voltar ao último diretório |
| `Tab` / `Espaço` | Marcar item |
| `Insert` | Enviar para fila 1, 2 ou 3 |
| `Ctrl-P` | Alternar filas 1→2→3→diretório |
| `Ctrl-F` | Busca recursiva por extensão, tamanho e conteúdo |
| `Ctrl-D` | Buscar duplicados ou reabrir a lista temporária |
| `Ctrl-B` | Downloads |
| `Ctrl-K` | Menu completo de ações, manutenção e `Conversões` |
| `Ctrl-L` | Ir à pasta do arquivo |
| `Ctrl-/` | Ligar/desligar preview |
| `Del` | Remover conforme o contexto |
| `Alt-D` | Apagar do disco em playlist/fila |
| `F9` | Configuração e overview do sistema |
| `F10` | HELP EXPANDIDO com atalhos e manutenção |
| `F12` | Duplicados: selecionar uma amostra por grupo |
| `Ctrl-R` | Duplicados: inverter seleção |
| `Ctrl-A` / `Ctrl-X` | Duplicados: selecionar todos / limpar todos |
| `Q` / `X` | Sair do programa |

O menu `Ctrl-K` inclui manutenção de sistema, análise e limpeza de HD, SMART, SWAP, som, vídeo/GPU, remoção de diretórios vazios, overview, monitoramento de temperatura da CPU e o item `Conversões`. O item `Conversões` oferece vídeo→vídeo, imagem→imagem, imagens→PDF, PDF→imagem, PDF→texto e PDF→HTML; PDFs também podem ser abertos diretamente com `Enter`, e imagens aguardam uma pausa antes do retorno ao navegador.

## Duplicados e progresso

A busca de duplicados filtra primeiro por tamanho e depois compara o conteúdo por hash. Uma barra de progresso informa o andamento do inventário, cálculo dos hashes e consolidação dos grupos. A análise de HD e a limpeza automática também mostram o avanço por etapas.

## DRY-RUN e sudo

O estado do **DRY-RUN** é exibido no cabeçalho e nas telas de manutenção. Com o modo ligado, operações destrutivas são apenas simuladas. Quando uma operação exige `sudo`, o eazy abre uma caixa de senha antes da execução, autentica com `sudo -S` e executa o comando posterior com `sudo -n`, evitando prompts inesperados que possam quebrar a tela.

## Configuração

Os dados de usuário ficam em `~/.config/eazy/`, incluindo configuração, sessão, filas temporárias, histórico, seleções e listas de duplicados.

## Licença

Uso livre. Sem garantias.
