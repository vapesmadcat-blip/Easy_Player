# eazy 3.4.0 (release)

Navegador e reprodutor multimídia no **terminal** — fzf + mpv/mplayer/cvlc/ffplay.

**Repo:** https://github.com/vapesmadcat-blip/Easy_Player

## Destaques 3.3

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

## IA integrada

O eazy inclui um chat opcional via API compatível com OpenRouter. Configure a chave
sem gravá-la no código:

```bash
export EAZY_AI_API_KEY="sua-chave"
eazy --ai
```

Também é possível criar `~/.config/eazy/ai.env` com permissão `600`:

```text
EAZY_AI_API_KEY=sua-chave
EAZY_AI_MODEL=gryphe/mythomax-l2-13b
```

O chat também pode ser aberto em **F9 → Abrir chat com IA**. A chave enviada ao
projeto não é incluída no código nem no pacote.

## Instalação rápida

```bash
sudo dpkg -i eazy_3.3.5_all.deb && sudo apt-get install -f
# GNOME: sudo apt install ./eazy-gnome_3.3.2_all.deb
# KDE Plasma: sudo apt install ./eazy-kde_3.3.2_all.deb
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
