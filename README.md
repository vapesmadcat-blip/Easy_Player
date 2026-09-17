# eazy 3.2.12 (release)

Navegador e reprodutor multimídia no **terminal** — fzf + mpv/mplayer/cvlc/ffplay.

**Repo:** https://github.com/vapesmadcat-blip/Easy_Player

## Destaques 3.2.12

- **Man page completa** no `.deb` e no `eazy --install`
- **Legenda de cores** na linha inferior (DIR / VID / AUD / IMG / ZIP / DOC)
- **Seleção global**: quantidade + bytes ao zerar; lista em F9
- **Extensões na pesquisa** no formato `INCLUIR MPG — CATEGORIA VIDEOS`
- **Links**: abrir no browser ou adicionar à fila (Ctrl+B); edição da fila
- **Exportar notas**, IA smithi (preferência), data/hora no status
- **Cache** de busca / listas / playlist
- **Limpeza** de caches (gradle, snap, …) na manutenção
- **Instalador** com detecção **GNOME** e **KDE** + deps do ambiente
- Pacote `.deb` compatível com GNOME e KDE Plasma

## Instalação rápida

```bash
sudo dpkg -i eazy_3.2.12_all.deb && sudo apt-get install -f
# ou
./eazy --install
```

Detalhes: [INSTALL.md](INSTALL.md) · Ajuda: `man eazy` · `eazy --help`

## Atalhos principais

| Tecla | Ação |
|-------|------|
| Enter | Tocar / entrar na pasta |
| Tab · Espaço | Marcar (persistente) |
| Ctrl+F | Busca recursiva |
| Ctrl+D | Duplicados |
| Ctrl+B | Downloads (editar / adicionar) |
| Ctrl+P | Filas / playlists |
| F9 | Configuração + overview |
| F10 | Ajuda |
| Alt+Enter | Executar seleção acumulada |
| Q | Sair |

## Cores na lista

| Cor | Tipo |
|-----|------|
| Azul | Diretório |
| Ciano | Vídeo |
| Amarelo | Áudio / playlist |
| Magenta | Imagem |
| Vermelho | Compactado |
| Verde | Documento / outros |

## Documentação

- `EAZY_EXPLICADO.md` — visão detalhada
- `GUIA_RAPIDO.md` — referência rápida
- `CHANGELOG.md` — histórico
- `man eazy` — manual instalado

## Licença

Uso livre. Sem garantias.
