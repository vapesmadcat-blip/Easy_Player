# Easy Player 5.2.0

Navegador e reprodutor multimídia no terminal, com seleção persistente, filas e listas temporárias SQLite, histórico SQLite, downloads, manutenção, IA, editor de notas, torrents e Central de streaming.

**Canal atual:** a branch `main` contém a versão beta testada **5.2.0 rev.56**. A tag/release `v5.2.0` e o instalador Debian abaixo permanecem na versão estável publicada; a atualização desta branch não substitui nem sobrescreve essa release. Para obter a beta em `~/.local/bin`, use `install-eazy-pronto.sh`.

## Executar sem instalação

Para testar uma cópia descompactada, execute `./run-beta.sh` (ou `./eazy`) com `eazy-index.py` ao lado do programa. Isso não instala nada.

## Instalação

```bash
curl -fsSL https://raw.githubusercontent.com/vapesmadcat-blip/Easy_Player/main/install-from-web.sh | bash
```

Instalação manual pelo pacote Debian:

```bash
curl -fLO https://github.com/vapesmadcat-blip/Easy_Player/releases/download/v5.2.0/eazy_5.2.0_all.deb
curl -fLO https://github.com/vapesmadcat-blip/Easy_Player/releases/download/v5.2.0/eazy_5.2.0_all.deb.sha256
sha256sum -c eazy_5.2.0_all.deb.sha256
sudo apt install ./eazy_5.2.0_all.deb
```

## Instalação da beta rev.56

Para instalar a beta da branch `main` no diretório do usuário, sem `sudo`:

```bash
curl -fsSL https://raw.githubusercontent.com/vapesmadcat-blip/Easy_Player/main/install-eazy-pronto.sh | bash
```

## Persistência local SQLite

O banco padrão fica em `~/.config/eazy/eazy-index.sqlite3`. O histórico e as filas/listas temporárias são armazenados em tabelas SQLite. Arquivos de texto em `~/.config/eazy/tmp/` são snapshots efêmeros usados somente para compatibilidade com componentes que consomem linhas; não são a fonte persistente. O cabeçalho e o menu Ctrl+P usam o nome lógico da lista.

Na primeira entrada no Histórico, por `Ctrl+G` ou `Ctrl+P`, o Easy lê o arquivo legado `~/.config/eazy/history`, recria a tabela de histórico e preserva intacto o arquivo original. A primeira tentativa conclui a migração e retorna; abra o Histórico novamente.

Para migrar filas/listas antigas `temp_playlist_*` antes de usar a versão SQLite, feche o Easy e execute o migrador incluído na distribuição. Primeiro confira a prévia e depois aplique:

```bash
python3 migrate_eazy_lists.py
python3 migrate_eazy_lists.py --apply
```

No pacote Debian, o migrador fica em `/usr/lib/eazy/migrate_eazy_lists.py`. O migrador cria backup do banco existente antes de gravar e não apaga os arquivos legados. Não use `--replace` a menos que tenha verificado a prévia e queira substituir o conteúdo SQL divergente pelo arquivo original.

## Streaming

A Central abre com `eazy --stream` ou pelo menu de streams do `Ctrl-B`. Usa `yt-dlp`, apresenta duração e paginação, mantém pesquisas e histórico de filmes assistidos, permite favoritos e inclui fontes públicas de filmes e TV aberta.

## Componentes

A distribuição beta inclui `eazy`, `eazy-index.py`, `eazy-convert-m3u.py`, `eazy-live-watch.py`, `full.c`, `migrate_eazy_lists.py`, `eazy-yt-stream`, `eazy-tor`, `eazy-ai.py`, `eazy-notes-editor`, launcher desktop, man page e Help HTML/TXT. Os instaladores colocam os componentes nos caminhos de sistema ou do usuário sem caminhos de usuário fixos.

## Desenvolvimento e validação

```bash
bash -n eazy eazy-yt-stream install-eazy-pronto.sh packaging/eazy/build-deb.sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
bash tests/test_cleanup_empty_items.sh
bash tests/test_copy_move_selection_scope.sh
bash tests/test_copy_tree_conflicts.sh
./packaging/eazy/build-deb.sh
make dist
./eazy --version
./eazy --help
```

**Made by John B Kersting.**
