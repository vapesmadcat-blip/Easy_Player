# Instalação do eazy

## Debian / Ubuntu — versão 3.0-60

A instalação oficial usa a **Release do GitHub**, o pacote `.deb` e seu checksum SHA-256:

```bash
curl -fLO https://github.com/vapesmadcat-blip/Easy_Player/releases/download/eazy-v3.0-60/eazy_3.0-60_all.deb
curl -fLO https://github.com/vapesmadcat-blip/Easy_Player/releases/download/eazy-v3.0-60/eazy_3.0-60_all.deb.sha256
sha256sum -c eazy_3.0-60_all.deb.sha256
sudo apt install ./eazy_3.0-60_all.deb
eazy
```

O comando `sha256sum -c` deve informar `OK` antes da instalação. Não instale o pacote se a verificação falhar.

Para remover os arquivos baixados depois da instalação:

```bash
rm -f eazy_3.0-60_all.deb eazy_3.0-60_all.deb.sha256
```

## Atualização a partir do código

```bash
git clone https://github.com/vapesmadcat-blip/Easy_Player.git
cd Easy_Player
chmod +x packaging/build-deb.sh
./packaging/build-deb.sh
sha256sum packaging/eazy/dist/eazy_3.0-60_all.deb
sudo apt install ./packaging/eazy/dist/eazy_3.0-60_all.deb
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
  axel aria2 unzip p7zip-full rar yt-dlp lm-sensors poppler-utils img2pdf
```

Recursos opcionais: `chafa`, `ffmpeg`, `vlc`, `smartmontools`, `pciutils`, `lshw`, `inxi`, `dmidecode`, `usbutils`, `mesa-utils` e `vulkan-tools`.

### Busca avançada por nome e conteúdo

No `Ctrl-F`, informe extensões, nomes e curingas separados por espaço ou vírgula. Exemplos: `sh mp4 vid* filme.mov movie.*`. Extensões simples viram `*.ext`; padrões com ponto ou curingas são tratados como nomes completos.

Para filtrar o conteúdo, escolha **Sim — digitar uma ou mais palavras-chave** e informe uma expressão. Palavras simples separadas por espaço equivalem a `AND`; `OR` aceita alternativas; `NOT` exclui o termo seguinte. Frases entre aspas preservam os espaços. Exemplos: `alpha beta`, `alpha OR beta`, `"erro grave" AND NOT debug`.

A ordem é: primeiro o eazy encontra os arquivos pelo nome/extensão, depois verifica a expressão no conteúdo de cada arquivo e só então mostra a lista. Pesquisas salvas preservam a expressão e o snapshot; `Alt-R` solicita uma nova execução.

## Recursos da versão 3.0-60

O editor de notas agora é o mini editor visual incluído no pacote, sem dependência de Vim, vi ou nano. Seus atalhos são `Ctrl-N` para nova nota, `Ctrl-S` para salvar e abrir outra, `Esc` para salvar e sair, `Enter` para nova linha e `Backspace` para apagar. O gerenciador mantém `Ctrl-E`, `Del`, `Ctrl-R` e `Ctrl-X` para listar, apagar, renomear e exportar notas.

A atualização inclui HELP EXPANDIDO no `F10`, saída com `Esc` da busca recursiva, barras de progresso na busca de duplicados e na limpeza/análise do HD, menu `Ctrl-K` completo, monitoramento de temperatura da CPU, autenticação sudo por caixa de senha e indicador persistente de DRY-RUN.

## PDF: leitura e conversão

Ao selecionar um arquivo `.pdf` e pressionar `Enter`, o eazy abre uma caixa para escolher leitura do texto no terminal, conversão para HTML, conversão das páginas para PNG ou abertura no leitor gráfico do sistema. O menu `Ctrl-K → C — Conversões` oferece vídeo→vídeo, imagem→imagem, imagens→PDF e PDF→imagem. Imagens abertas no terminal aguardam `Enter` antes de retornar ao navegador.

As ferramentas usadas são `pdftotext`, `pdftohtml`, `pdftoppm` e `img2pdf`, fornecidas por `poppler-utils` e `img2pdf`.

## Verificação

```bash
eazy --version
eazy --help
```

O arquivo de configuração e os dados da sessão ficam em `~/.config/eazy/` e não são removidos durante a atualização do pacote. A limpeza automática solicita a idade em dias, mostra uma prévia e só remove itens após uma segunda confirmação.
