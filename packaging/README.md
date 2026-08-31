# eazy — pacote Debian

Este diretório contém o empacotamento Debian do **eazy 3.0 (professional)**, um navegador e reprodutor multimídia no terminal.

## Instalação pelo GitHub Release

A release atual `eazy-v3.0-77` está publicada. Em Debian ou Ubuntu, execute:

```bash
curl -fLO https://github.com/vapesmadcat-blip/Easy_Player/releases/download/eazy-v3.0-77/eazy_3.0-77_all.deb
curl -fLO https://github.com/vapesmadcat-blip/Easy_Player/releases/download/eazy-v3.0-77/eazy_3.0-77_all.deb.sha256
sha256sum -c eazy_3.0-77_all.deb.sha256
sudo apt install ./eazy_3.0-77_all.deb
```

O `apt` instala automaticamente as dependências declaradas pelo pacote. O comando fica disponível como `eazy`, e o launcher gráfico é instalado em `/usr/share/applications/eazy.desktop`. Ao selecionar um arquivo `.m3u` e pressionar Enter, o eazy abre a playlist no navegador interno. O menu F9 também oferece um overview do sistema (OS, RAM, discos, drives, áudio e vídeo) e um teste de som. No modo Duplicados, a seleção fica em uma lista temporária persistente: F12 seleciona um arquivo por grupo e marca esses itens com ✓; Tab/Espaço alternam a seleção manual; Ctrl-A seleciona todos; Ctrl-X limpa todos; e Ctrl-R inverte a seleção atual. O cabeçalho mostra continuamente a quantidade e o total de bytes selecionados, mesmo após redesenhos da lista.

Para testar:

```bash
eazy --version
eazy --help
eazy ~/Videos
```

Para remover o programa, preservando a configuração do usuário:

```bash
sudo apt remove eazy
```

Os dados de sessão e configuração ficam em `~/.config/eazy/`.

## Recursos documentados na versão 3.0-77

A versão 3.0-77 inclui busca por extensões, nomes e curingas combinada com busca por conteúdo usando **frases entre aspas** e operadores lógicos `AND`, `OR` e `NOT`, além da validação de playlists, listas temporárias e pesquisas salvas. Quando a validação encontra referências ausentes, o eazy pergunta se o usuário deseja corrigir; a confirmação é obrigatória e a correção remove somente entradas quebradas, sem apagar arquivos físicos do disco. O pacote também inclui o mini editor visual de notas, sem dependência de Vim, vi ou nano. No release 3.0-57, Ctrl-S salva a lista temporária atualmente aberta, inclusive listas personalizadas, em vez de cair indevidamente na fila 1. No release 3.0-77, a limpeza automática solicita a idade dos arquivos em dias, mostra uma prévia e exige confirmação final antes de remover itens. A versão 3.0-77 consolida essa documentação com exemplos da busca avançada.

## Dependências opcionais

Para habilitar downloads, previews, formatos adicionais e um diagnóstico de hardware mais completo, podem ser instalados `yt-dlp`, `aria2`, `axel`, `chafa`, `ffmpeg`, `p7zip-full`, `rar`, `pciutils`, `alsa-utils`, `pulseaudio-utils`, `lshw`, `smartmontools`, `dmidecode`, `inxi`, `usbutils`, `x11-xserver-utils`, `mesa-utils`, `vulkan-tools`, `iw`, `network-manager`, `upower` e `lm-sensors`. O pacote exige apenas o conjunto mínimo para iniciar o navegador e tocar mídia. O overview funciona sem os opcionais e marca como indisponíveis as informações que dependem deles.

## Construção local

A partir da raiz deste repositório:

```bash
chmod +x packaging/build-deb.sh packaging/eazy/build-deb.sh
./packaging/build-deb.sh
```

O resultado será gerado em `packaging/eazy/dist/eazy_3.0-77_all.deb`. Para inspecionar o pacote sem instalá-lo:

```bash
dpkg-deb --info packaging/eazy/dist/eazy_3.0-77_all.deb
dpkg-deb --contents packaging/eazy/dist/eazy_3.0-77_all.deb
```

## Origem dos arquivos

O pacote usa os arquivos fornecidos para esta publicação: `eazy`, `eazy.desktop`, `README.md`, `CHANGELOG.md`, `EAZY_EXPLICADO.md` e `GUIA_RAPIDO.md`. O binário instalado é `/usr/bin/eazy`; os documentos ficam em `/usr/share/doc/eazy/`.
