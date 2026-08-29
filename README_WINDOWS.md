# eazy 3.0 para Windows

Esta é a versão Python do eazy 3.0 para Windows. Ela mantém o objetivo central do projeto: navegar, localizar, reproduzir e organizar arquivos multimídia em um único fluxo de trabalho. A implementação usa apenas a biblioteca padrão do Python; não há dependências obrigatórias de Linux, `bash`, `fzf`, `whiptail`, `sudo`, `apt` ou `tput`.

## Requisitos

É necessário ter **Python 3.10 ou superior** instalado no Windows. O instalador oficial pode ser obtido em [python.org](https://www.python.org/downloads/windows/). Durante a instalação, ative a opção **Add Python to PATH**.

Para confirmar:

```powershell
py --version
```

## Execução

Abra o PowerShell na pasta do projeto e execute:

```powershell
py eazy_windows.py
```

Para iniciar em uma pasta específica:

```powershell
py eazy_windows.py "C:\Users\SeuNome\Videos"
```

Para iniciar com um arquivo:

```powershell
py eazy_windows.py "C:\Users\SeuNome\Videos\filme.mp4"
```

## Comandos diretos

```powershell
py eazy_windows.py --version
py eazy_windows.py --help
py eazy_windows.py --search "relatorio"
py eazy_windows.py --duplicates "C:\Users\SeuNome\Documents"
```

## Funcionalidades incluídas

A versão Windows inclui navegador de arquivos e diretórios, ordenação por nome, tamanho e data, seleção múltipla, cópia e movimentação por meio das rotinas do Windows, abertura de arquivos com o aplicativo padrão, histórico, filas, playlists `.m3u`, busca recursiva por nome, extensão, conteúdo e tamanho, detecção de duplicados por tamanho e SHA-256, validação de playlists, limpeza de diretórios vazios, notas rápidas e persistência da configuração.

Os dados do usuário são armazenados em:

```text
%APPDATA%\eazy\
```

Nesse diretório ficam as configurações, histórico, filas, pesquisas salvas e notas. As playlists permanentes são gravadas em:

```text
%USERPROFILE%\Playlists\
```

## Atalhos do menu

| Comando | Função |
|---|---|
| Número | Abrir pasta ou arquivo selecionado |
| `S` | Busca recursiva |
| `D` | Encontrar duplicados |
| `Q` | Salvar itens em fila |
| `P` | Criar playlist `.m3u` |
| `N` | Gerenciar notas |
| `M` | Abrir manutenção |
| `O` | Alternar ordenação |
| `X` | Salvar sessão e sair |

## Reprodução multimídia

O eazy tenta usar `mpv`, VLC ou Windows Media Player, nesta ordem de disponibilidade. Para obter melhor suporte a formatos, instale [mpv para Windows](https://mpv.io/installation/) e deixe o executável acessível no `PATH`. Sem um player externo, o Windows abrirá o arquivo com o aplicativo padrão associado à extensão.

## Limites da primeira versão Windows

Alguns recursos originalmente dependentes de ferramentas Linux foram adaptados para o ambiente Windows. O diagnóstico de hardware via `SMART`, `SWAP`, `sudo`, `whiptail` e os fluxos específicos de `chafa`, `pdftotext`, `ffmpeg` e `yt-dlp` não são obrigatórios nesta primeira versão. Quando uma ferramenta externa não está instalada, o eazy usa o aplicativo padrão do Windows ou informa que o recurso opcional não está disponível.

A versão Python é uma base nativa e extensível para Windows; ela não substitui automaticamente o script Bash Linux em todos os detalhes de interface e manutenção de sistema.

## Próximas extensões possíveis

A arquitetura permite adicionar uma interface gráfica Tkinter, integração direta com FFmpeg, suporte a busca lógica `AND`/`OR`/`NOT`, editor de notas multilinha, exportação para `.exe` com PyInstaller e um instalador Windows.
