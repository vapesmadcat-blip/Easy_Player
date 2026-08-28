# eazy — documentação completa de funcionamento e vantagens

## 1. O que é o eazy

O **eazy** é um navegador, organizador e reprodutor multimídia para o terminal. Ele foi desenvolvido em Bash e utiliza o `fzf` como interface interativa de navegação e seleção. O programa permite administrar arquivos de áudio, vídeo, imagens, PDFs, textos, playlists e diretórios sem precisar alternar continuamente entre o gerenciador de arquivos, o player, ferramentas de busca e programas de conversão.

A interface é orientada principalmente pelo teclado, mas também permite seleção por mouse quando o terminal oferece esse recurso. O cabeçalho mostra o diretório atual, o modo de ordenação, o estado do DRY-RUN, o espaço do disco e as informações da seleção.

A ideia central é simples: **navegar, localizar, selecionar e executar ações sobre arquivos em um único fluxo**. O eazy também preserva o contexto do usuário, incluindo sessão, cursor, listas temporárias, histórico, pesquisas, notas e últimos destinos de cópia e movimentação.

## 2. Inicialização e ciclo principal

Ao iniciar, o eazy carrega as configurações gravadas em `~/.config/eazy`. Em seguida, recupera o diretório da última sessão, a ordem de exibição, o modo de tela, o volume, o player escolhido, o estado do preview e a posição persistente do cursor.

A lista de arquivos é montada novamente a cada ciclo do navegador. Diretórios aparecem no topo e podem ser acessados pelo item `..`, que representa o diretório pai. Ao entrar em uma pasta, o eazy atualiza a listagem, limpa o filtro da tela atual e mantém as seleções conforme o comportamento configurado. Ao retornar a um diretório anterior, o programa restaura a posição registrada para aquele local quando o fluxo de navegação permite.

O fzf trabalha em modo de seleção múltipla. O item visual contém campos separados para ordenação, nome exibido, tamanho e caminho real. Dessa forma, o eazy consegue mostrar um nome amigável sem perder o caminho absoluto usado pelas ações de abrir, reproduzir, copiar, mover ou apagar.

## 3. Filtro e ordenação

O filtro do fzf permite localizar rapidamente nomes de arquivos e diretórios. A busca ocorre sobre a lista atual e pode ser combinada com os modos de ordenação disponíveis.

| Modo | Resultado |
|---|---|
| Tamanho | Ordena pelos bytes do item |
| Nome | Ordena alfabeticamente |
| Data | Ordena pela data do arquivo |
| Especial | Usado em filas, playlists, downloads e listas específicas |

O preview pode ser ligado ou desligado. Quando ativo, o eazy tenta mostrar informações do arquivo e uma visualização adequada ao tipo: imagem, PDF, texto, áudio, vídeo ou arquivo compactado.

## 4. Seleção de arquivos e diretórios

A seleção múltipla é uma das funções centrais do eazy. Arquivos e diretórios podem ser selecionados para reprodução, cópia, movimentação, exclusão, inclusão em filas, análise ou conversão.

| Tecla | Ação |
|---|---|
| `Tab` | Seleciona o item atual e avança para o próximo |
| `Shift-Tab` | Seleciona o item atual e volta para o anterior |
| `Espaço` | Marca ou desmarca o item atual sem avançar |
| `Enter` | Abre, reproduz, entra no diretório ou confirma a ação |
| `Ctrl-A` | Seleciona todos, conforme o contexto |
| `Ctrl-X` | Limpa a seleção em contextos que usam essa ação |
| `Del` | Executa a remoção correspondente ao modo atual |

A seleção pode conter diretórios. Uma pasta selecionada é reconhecida como diretório, recebe ícone próprio, tem tamanho calculado recursivamente e não é tratada como uma mídia comum pelo player.

O cabeçalho informa a quantidade de itens selecionados e os bytes ocupados. Para um arquivo, o cálculo usa o tamanho do arquivo. Para uma pasta, o cálculo considera o conteúdo recursivo da pasta.

## 5. Navegação entre diretórios

O item `..` aparece no topo da listagem e representa o diretório pai. Pressionar `Enter` sobre ele sobe um nível. Ao entrar em um diretório a partir do navegador normal, o eazy registra a posição atual e prepara a nova listagem.

O atalho `Ctrl-Backspace` é utilizado para retornar ao último diretório visitado. Quando existe posição registrada para o diretório anterior, o eazy tenta restaurar o cursor naquele ponto. O comportamento é diferente do uso de `..`: entrar em `..` representa uma subida hierárquica, enquanto `Ctrl-Backspace` representa o retorno ao local anterior visitado.

Quando um diretório é aberto a partir de uma lista temporária ou playlist, o eazy registra a lista de origem. Ao pressionar `..` para sair da pasta, o programa retorna à lista de origem em vez de abandonar o modo da lista e voltar ao navegador principal.

## 6. Reprodução multimídia

O eazy reconhece vários tipos de arquivo e escolhe o fluxo adequado. O player padrão pode ser alterado na configuração.

| Player | Uso |
|---|---|
| `mpv` | Player padrão recomendado, com suporte a playlists e script de exclusão |
| `mplayer` | Alternativa tradicional para áudio e vídeo |
| VLC CLI | Reprodução por `cvlc` quando configurado |
| `ffplay` | Reprodução individual e conversões baseadas em FFmpeg |

Arquivos de áudio e vídeo são enviados ao player configurado. Quando vários arquivos são selecionados, o eazy monta uma lista temporária e envia a seleção ao player. A ordem pode ser mantida ou embaralhada pelo modo aleatório.

Arquivos de imagem são exibidos com preview no terminal quando `chafa` ou outra ferramenta compatível está disponível. Depois da visualização, o eazy aguarda uma confirmação para que a tela permaneça disponível e o usuário consiga observar a imagem antes de retornar ao navegador.

Arquivos de texto podem ser lidos diretamente no terminal. Playlists `.m3u` e formatos compatíveis podem ser abertas no navegador de playlists.

## 7. Filas temporárias

O eazy possui três filas temporárias independentes. Elas funcionam como listas de reprodução rápidas e persistentes entre sessões.

| Fila | Arquivo interno |
|---|---|
| Fila 1 | `~/.config/eazy/temp_playlist_1` |
| Fila 2 | `~/.config/eazy/temp_playlist_2` |
| Fila 3 | `~/.config/eazy/temp_playlist_3` |

O menu `Insert` envia a seleção atual para uma das filas. O usuário pode escolher substituir, acrescentar ou operar sobre o destino conforme o diálogo apresentado. As filas podem conter arquivos e diretórios. Arquivos são reproduzidos normalmente; diretórios são reconhecidos como pastas e podem ser abertos.

O `Ctrl-P` percorre as filas temporárias e as listas personalizadas. O cabeçalho mostra o nome da fila e a quantidade de itens. A fila atual também pode ser usada para salvar uma playlist permanente.

## 8. Listas temporárias personalizadas

Além das três filas padrão, o menu `Insert` permite criar uma nova lista temporária nomeada. O usuário informa o nome e o eazy grava a lista em um arquivo seguro.

As listas personalizadas aparecem no `Insert` e no ciclo do `Ctrl-P`. O nome exibido é o nome fornecido pelo usuário, acompanhado da quantidade de itens. Identificadores internos não são mostrados.

| Exemplo visual | Significado |
|---|---|
| `lista-nova2 — 4 itens` | Lista personalizada chamada `lista-nova2` |
| `minhas-musicas — 28 itens` | Lista personalizada com 28 entradas |

Os arquivos ficam em `~/.config/eazy/temp_playlist_custom_NOME`. Espaços e caracteres incompatíveis com nomes de arquivo são normalizados no momento da criação.

Se uma lista personalizada contiver um diretório, esse diretório aparece como pasta. Pressionar `Enter` nele abre a pasta; pressionar `..` depois retorna à lista que estava aberta antes da navegação.

## 9. Playlists permanentes

O eazy pode salvar uma fila como playlist permanente. O fluxo pede a pasta de destino e o nome do arquivo. A pasta padrão é `~/Playlists`, mas outra localização pode ser informada.

As playlists podem ser abertas pelo menu correspondente ou pelo navegador de arquivos. O eazy resolve caminhos relativos usando a pasta onde a playlist está armazenada e mantém caminhos absolutos quando eles já existem.

| Operação | Resultado |
|---|---|
| Salvar playlist | Grava a fila em arquivo permanente |
| Abrir playlist | Exibe os itens em modo de playlist |
| Validar playlist | Remove referências inexistentes |
| Limpar playlist | Reescreve a playlist apenas com entradas válidas |
| Fechar playlist | Retorna ao navegador principal |

Durante a validação, uma barra de progresso informa o andamento. O resultado mostra linhas originais, entradas removidas e entradas mantidas.

Diretórios dentro de uma playlist são mostrados como pastas, com tamanho recursivo e navegação. Eles não são tratados como arquivos de mídia.

## 10. Pesquisa recursiva

O `Ctrl-F` abre a pesquisa recursiva. Ela pode localizar arquivos por extensão, tamanho e conteúdo.

| Critério | O que faz |
|---|---|
| Extensão | Limita a busca a tipos como áudio, vídeo, imagem, PDF ou texto |
| Tamanho mínimo | Encontra arquivos acima de um limite |
| Tamanho máximo | Encontra arquivos abaixo de um limite |
| Faixa de tamanho | Combina limites mínimo e máximo |
| Conteúdo | Procura texto dentro de arquivos compatíveis |
| Nome/filtro | Refina os resultados exibidos pelo fzf |

A pesquisa mostra o tipo, o nome, o tamanho e o caminho encontrado. Os resultados podem ser selecionados individualmente ou em múltiplos itens para reprodução, cópia, movimentação, exclusão e inclusão em filas.

O `Esc` encerra o modo de pesquisa e retorna ao navegador normal. O mesmo princípio vale para telas de leitura, preview, escolha de arquivo, conversões, diagnósticos e diálogos: quando a tela está aguardando interação ou oferece cancelamento, `Esc` interrompe a operação e retorna ao contexto anterior. O resultado não precisa ser digitado manualmente: a seleção é transformada em caminhos reais pelo eazy.

O sistema utiliza cache temporário durante a pesquisa para evitar trabalho repetido na mesma sessão. Esse cache fica em `/tmp` e não é tratado como dado permanente do usuário. O snapshot permanente de cada pesquisa fica junto do arquivo `.search`, com extensão `.results.tsv`, dentro de `~/.config/eazy/saved_searches/`.

## 11. Pesquisas salvas

Uma pesquisa configurada pode ser salva com um nome. O eazy armazena extensão, tamanho mínimo, tamanho máximo, conteúdo pesquisado e demais parâmetros necessários para reabrir o mesmo filtro posteriormente. Além dos parâmetros, ele grava um **snapshot do resultado encontrado** no momento do salvamento.

Ao abrir uma pesquisa salva, o resultado congelado é mostrado imediatamente e a busca não é refeita. Isso preserva o resultado original mesmo que arquivos tenham sido criados, movidos ou alterados depois. Dentro da lista, `Alt-R` solicita um **remake**, descartando o snapshot e executando novamente a pesquisa. Na tela de escolha de uma pesquisa salva, o usuário também pode confirmar que deseja refazê-la.

As pesquisas ficam em:

```text
~/.config/eazy/saved_searches/
```

Ao abrir novamente o menu de pesquisa, o usuário pode iniciar uma pesquisa nova ou escolher uma pesquisa salva. Isso é útil para consultas repetitivas, como encontrar vídeos grandes, localizar PDFs, procurar gravações de áudio ou localizar arquivos contendo determinada palavra.

## 12. Histórico de arquivos tocados

O eazy mantém um histórico dos arquivos reproduzidos. O histórico pode ser aberto pelo menu de playlists/histórico e funciona como uma lista navegável.

O histórico permite rever rapidamente arquivos usados recentemente, reproduzir novamente uma entrada, selecionar várias entradas e remover registros. A limpeza do histórico não apaga os arquivos do disco; remove apenas as referências armazenadas pelo eazy.

O arquivo do histórico fica em:

```text
~/.config/eazy/history
```

## 13. Sistema de arquivos duplicados

O módulo de duplicados procura arquivos repetidos. Primeiro, o eazy pode agrupar candidatos por tamanho; depois, compara o conteúdo usando hash para confirmar os grupos.

O processo apresenta progresso durante o inventário, a comparação e a consolidação. Os grupos duplicados podem ser examinados e selecionados visualmente.

| Marca | Significado |
|---|---|
| `●` vermelho | Amostra fixa, normalmente criada pelo F12 |
| `✓` amarelo | Seleção ativa usada pelas ações |

| Atalho | Ação no modo de duplicados |
|---|---|
| `F12` | Seleciona uma amostra por grupo |
| `Ctrl-T` | Transforma a amostra vermelha em seleção amarela |
| `Ctrl-A` | Seleciona todos os arquivos apresentados |
| `Ctrl-R` | Inverte a seleção amarela |
| `Ctrl-X` | Limpa a seleção amarela |
| `Tab` / `Espaço` | Alterna a seleção do item |
| `Enter` | Reproduz ou usa a seleção conforme o contexto |
| `Del` | Remove a seleção conforme a confirmação apresentada |

O eazy separa a amostra fixa da seleção ativa. Assim, é possível manter uma referência visual do grupo e escolher independentemente quais itens serão usados pela ação.

## 14. Copiar e mover arquivos

`Ctrl-Y` copia a seleção e `Ctrl-U` move a seleção. O eazy pede ou apresenta um destino e verifica se a pasta existe. Quando necessário, o programa pode criar o destino.

O último destino de cópia é persistido separadamente do último destino de movimentação:

```text
~/.config/eazy/last_copy_destination
~/.config/eazy/last_move_destination
```

Essa separação permite copiar repetidamente para uma pasta sem substituir o destino usado para mover. O destino fica disponível para a próxima operação e pode ser alterado quando necessário.

Antes de operar, o eazy calcula o espaço necessário, compara com o espaço livre e mostra informações do disco. Diretórios selecionados são tratados como árvores de arquivos para calcular o tamanho.

## 15. Exclusão e limpeza de arquivos

A tecla `Del` executa uma ação conforme o modo atual. No navegador, pode iniciar uma operação de limpeza ou exclusão. Em filas e playlists, pode remover itens da lista sem necessariamente apagar o arquivo físico. No modo de duplicados, pode operar sobre a seleção duplicada.

`Alt-D` é usado para apagar diretamente do disco em contextos de playlist ou fila, quando essa ação é explicitamente escolhida. O eazy mostra confirmação antes de operações destrutivas e respeita o modo DRY-RUN.

Quando a operação envolve muitos arquivos, o sistema apresenta contagem, tamanho e progresso. Falhas são informadas individualmente quando possível.

## 16. Downloads

O `Ctrl-B` abre o gerenciador de downloads. O eazy oferece integração com diferentes motores, conforme instalados:

| Motor | Uso |
|---|---|
| `axel` | Download segmentado |
| `aria2c` | Download avançado e multiconexão |
| `wget` | Alternativa tradicional |
| `curl` | Alternativa disponível em vários sistemas |
| `yt-dlp` | Conteúdo compatível com plataformas de vídeo |

As filas de download são persistentes e podem armazenar motor, link e parâmetros. O eazy mostra o estado da fila, permite remover itens e trata credenciais ou senhas com cuidado, sem exibir o valor em claro na interface.

O `yt-dlp` pode ser atualizado pelo próprio programa com `--update-ytdlp`, usando `~/.local/bin`.

## 17. Menu de ações — Ctrl-K

O `Ctrl-K` abre o menu completo de ações e manutenção. Ele reúne operações sobre seleção, arquivos, playlists, sistema e conversões.

### 17.1 Sistema

A área de sistema apresenta informações sobre CPU, memória RAM, cache, processos, rede e logs. Serve para diagnóstico rápido sem sair do eazy.

### 17.2 HD e armazenamento

A área de HD permite consultar espaço, partições, ocupação e saúde do armazenamento. O eazy mostra espaço livre e total e utiliza essas informações antes de operações que gravam ou movem muitos dados.

A limpeza de temporários pode analisar `/tmp`, `~/.cache`, a lixeira do usuário e arquivos temporários locais. A execução exibe progresso por etapas e pede confirmação.

### 17.3 SMART

Quando `smartctl` está disponível, o menu de HD pode consultar informações SMART dos dispositivos. O objetivo é indicar saúde, temperatura, setores problemáticos e dados básicos do dispositivo. Operações que exigem privilégios são autenticadas antes da execução.

### 17.4 Áudio

A área de som verifica ferramentas, dispositivos e configuração de áudio. Também pode reiniciar componentes de áudio ou executar um teste sonoro quando as ferramentas do sistema estão disponíveis.

### 17.5 Vídeo e GPU

A área de vídeo reúne informações de GPU, codecs, aceleração, ferramentas gráficas, reprodução e otimizações. O eazy pode exibir o que está disponível no sistema e indicar pacotes ausentes.

### 17.6 SWAP

A área de SWAP mostra o estado atual e oferece ações de criação, configuração, limpeza ou ajuste quando permitido. Como são operações administrativas, o eazy usa confirmação, autenticação e indicação de DRY-RUN.

### 17.7 Temperatura da CPU

O diagnóstico térmico utiliza sensores do sistema, especialmente `lm-sensors` quando instalado, e pode consultar informações disponíveis no kernel. O menu mostra temperaturas detectadas e avisa quando uma ferramenta não está instalada.

### 17.8 Diretórios vazios

A função de diretórios vazios procura pastas sem conteúdo, permite revisar a lista e selecionar o que deve ser removido. O programa apresenta confirmação e respeita o DRY-RUN.

### 17.9 Validação de M3U

O eazy pode verificar referências de playlists `.m3u`, identificar entradas que não existem e gerar uma versão limpa. A operação mostra progresso e resumo final.

### 17.10 Proteção de arquivos e pastas

O menu inclui proteção de pasta ou arquivo com senha quando as ferramentas necessárias estão disponíveis. A ação pede os dados em diálogo apropriado e informa se a ferramenta de compactação ou proteção não estiver instalada.

### 17.11 Conversões

O item `C` ou `Conversões` concentra conversões de vídeo, imagem e PDF. Os arquivos são escolhidos na interface, evitando exigir que o usuário digite manualmente cada caminho.

## 18. Conversões de vídeo, imagem e PDF

O eazy integra FFmpeg, ImageMagick, img2pdf e Poppler quando instalados.

| Conversão | Ferramenta principal |
|---|---|
| Vídeo para vídeo | `ffmpeg` |
| Imagem para imagem | `magick` ou `convert` |
| Imagens para PDF | `img2pdf` |
| PDF para PNG | `pdftoppm` |
| PDF para texto | `pdftotext` |
| PDF para HTML | `pdftohtml` |

Ao pressionar `Enter` em um PDF, o eazy pode oferecer leitura do texto, conversão para HTML, conversão para imagens PNG ou abertura no leitor gráfico do sistema. A opção de conversão apresenta uma tela para selecionar o arquivo.

Para imagens, o programa oferece visualização com pausa. A pausa evita que a imagem desapareça imediatamente e permite retornar ao navegador somente depois da confirmação do usuário.

## 19. Notas rápidas

`Ctrl-N` abre a última nota editada. Se ainda não existir uma nota, o eazy cria ou abre `nota.txt`. O editor visual não depende de Vim, vi ou nano.

| Tecla | Função |
|---|---|
| `Ctrl-N` | Cria nova nota |
| `Ctrl-S` | Salva e abre outra nota |
| `Esc` | Salva e sai |
| `Enter` | Cria nova linha |
| `Backspace` | Apaga o caractere anterior |
| `Ctrl-E` | Abre a lista compacta de notas |
| `Del` | Apaga a nota escolhida |
| `Ctrl-R` | Renomeia a nota escolhida |
| `Ctrl-X` | Exporta para `~/Documentos/Easy-Notes/` |

A última nota editada fica registrada e é reaberta na próxima utilização. As notas ficam em:

```text
~/.config/eazy/notas/
```

A lista compacta permite localizar uma nota, abrir outra, apagar, renomear e exportar sem abandonar o editor.

## 20. Sessão, posição e persistência

O eazy grava a sessão ao sair pelos atalhos de saída. A sessão inclui diretório atual, modo de ordenação, filtros principais, modo de tela, preview, último arquivo e posição do cursor.

| Arquivo | Informação |
|---|---|
| `config` | Preferências gerais |
| `session` | Último estado da sessão |
| `dir_positions` | Posições salvas por diretório ou lista |
| `history` | Histórico de reprodução |
| `last_copy_destination` | Último destino de cópia |
| `last_move_destination` | Último destino de movimentação |
| `saved_searches/` | Pesquisas nomeadas |
| `notas/` | Notas rápidas |
| `temp_playlist_1` a `_3` | Filas temporárias |
| `temp_playlist_custom_*` | Listas nomeadas |

A persistência reduz a necessidade de refazer configurações e permite interromper o trabalho sem perder o contexto.

## 21. DRY-RUN e segurança

O modo **DRY-RUN** simula operações destrutivas ou administrativas sem aplicar alterações. O estado aparece no cabeçalho e nas telas de manutenção.

Quando uma operação exige `sudo`, o eazy abre uma caixa de senha antes de executar o comando. A senha não é gravada como configuração e o terminal é restaurado em caso de cancelamento ou falha.

O programa também verifica espaço em disco antes de operações de cópia, movimentação, compactação e conversão. Mensagens de erro são exibidas em diálogos, e o terminal pode emitir aviso sonoro em erros ou mudanças de diretório.

## 22. Atalhos gerais

| Atalho | Função |
|---|---|
| `Enter` | Abre arquivo, entra em pasta, toca ou confirma |
| `Tab` | Seleciona e avança |
| `Espaço` | Seleciona sem avançar |
| `Esc` | Cancela busca, leitura, preview ou diálogo interrompível |
| `Ctrl-Backspace` | Volta ao último diretório |
| `Ctrl-F` | Pesquisa recursiva |
| `Ctrl-B` | Downloads |
| `Ctrl-K` | Ações e manutenção |
| `Ctrl-L` | Vai à pasta do arquivo |
| `Ctrl-N` | Abre a última nota |
| `Ctrl-P` | Alterna filas e listas |
| `Ctrl-Y` | Copia seleção |
| `Ctrl-U` | Move seleção |
| `Ctrl-E` | Reprodução aleatória ou lista de notas conforme o contexto |
| `Ctrl-D` | Duplicados ou reabertura da lista temporária |
| `Ctrl-/` | Liga/desliga preview |
| `F9` | Configuração e overview do sistema |
| `F10` | HELP expandido |
| `F12` | Amostra de duplicados |
| `Del` | Remoção conforme o contexto |
| `Alt-D` | Exclusão direta do disco em filas/playlists |
| `Q`, `X` ou `Ctrl-Q` | Salva a sessão e sai |

## 23. Configuração e comandos de linha

| Comando | Função |
|---|---|
| `eazy` | Abre o navegador no diretório atual |
| `eazy /caminho` | Abre um diretório específico |
| `eazy arquivo.mp4` | Abre ou reproduz um arquivo |
| `eazy --help` | Ajuda resumida |
| `eazy --version` | Mostra a versão |
| `eazy --config` | Abre configuração |
| `eazy --install` | Instala dependências e o comando global |
| `eazy --uninstall` | Remove o comando instalado e o launcher local |
| `eazy --update-ytdlp` | Atualiza o yt-dlp em `~/.local/bin` |

## 24. Instalação e dependências

O pacote Debian declara as dependências básicas do navegador, incluindo Bash, fzf, whiptail, gawk, findutils, sed, um downloader e um player compatível. O instalador `--install` amplia esse conjunto para os recursos de PDF, conversão, preview, compactação, áudio, vídeo, rede e diagnóstico.

No Debian/Ubuntu, o instalador verifica e instala ferramentas como `fzf`, `mpv`, `mplayer`, `vlc`, `ffmpeg`, `whiptail`, `gawk`, `findutils`, `wget`, `curl`, `aria2`, `axel`, `yt-dlp`, `unzip`, `p7zip-full`, `imagemagick`, `poppler-utils`, `img2pdf`, `chafa`, `xdg-utils`, ferramentas de diagnóstico, ferramentas de áudio e ferramentas de GPU.

O pacote `rar` oficial pode depender da habilitação do repositório `non-free`; por isso é tratado como opcional. O eazy informa essa condição sem impedir a instalação do restante.

Além de copiar o comando global para `/usr/local/bin/eazy`, o `--install` instala o editor de notas em `/usr/lib/eazy/eazy-notes-editor`, instala o launcher quando encontrado e cria a estrutura inicial de dados do usuário.

## 25. Diretórios criados pelo instalador

O instalador cria ou prepara:

```text
~/.config/eazy/
~/.config/eazy/notas/
~/.config/eazy/saved_searches/
~/.config/eazy/mpv_scripts/
~/.config/eazy/scripts/
~/.config/eazy/backups/
~/Playlists/
~/Documentos/Easy-Notes/
```

Também inicializa as três filas temporárias, a lista de duplicados, o histórico e a fila de downloads. O cache de pesquisa permanece temporário em `/tmp` e é recriado conforme a sessão.

## 26. Vantagens do eazy

A primeira vantagem é a **integração**. Navegação, reprodução, pesquisa, filas, playlists, downloads, duplicados, conversões, manutenção e notas ficam acessíveis no mesmo ambiente.

A segunda é a **velocidade operacional**. A seleção por teclado, o Tab que seleciona e avança, o Espaço que marca sem avançar, as filas e os destinos persistentes reduzem ações repetitivas em coleções grandes.

A terceira é a **preservação de contexto**. O eazy mantém a última nota, histórico, pesquisas salvas, listas, posição de cursor e destinos de operação. O usuário pode interromper e retomar o trabalho sem reconstruir tudo.

A quarta é a **clareza visual**. O programa diferencia arquivos, pastas, imagens, áudio, vídeo, pacotes e itens ausentes. O cabeçalho mostra espaço do disco, estado do DRY-RUN, quantidade selecionada e bytes ocupados.

A quinta é a **segurança operacional**. Confirmações, verificação de espaço, autenticação controlada, restauração do terminal e DRY-RUN reduzem o risco de executar ações destrutivas por engano.

A sexta é o **tratamento correto de diretórios**. Pastas podem ser selecionadas, medidas recursivamente e abertas tanto no navegador quanto em listas temporárias. Elas não são confundidas com arquivos de mídia.

A sétima é a **portabilidade**. O projeto usa ferramentas tradicionais de Linux e pode trabalhar com diferentes players, gerenciadores de pacotes e utilitários auxiliares.

A oitava é a **auditabilidade**. Como o núcleo é um script Bash, o usuário pode ler, compreender, ajustar e verificar o comportamento. O pacote Debian simplifica a instalação, enquanto os dados pessoais ficam separados em `~/.config/eazy`.

## 27. Fluxos de uso recomendados

### Organizar uma pasta grande

Abra o diretório, use o filtro para localizar os itens, selecione com `Tab` ou `Espaço`, pressione `Ctrl-Y` para copiar ou `Ctrl-U` para mover e confirme o destino. O último destino será lembrado na próxima operação.

### Criar uma fila de reprodução

Selecione arquivos e diretórios no navegador, pressione `Insert`, escolha uma fila existente ou crie uma lista nomeada. Use `Ctrl-P` para abrir a lista, revisar os itens e reproduzir a seleção.

### Reutilizar uma pesquisa

Abra `Ctrl-F`, configure extensão, tamanho ou conteúdo, salve a pesquisa com um nome e reutilize-a posteriormente pelo menu de pesquisas salvas.

### Limpar duplicados

Abra o modo de duplicados, aguarde a análise, use `F12` para uma amostra por grupo, refine com `Ctrl-T`, `Ctrl-A`, `Ctrl-R` ou `Ctrl-X` e execute a ação somente depois de revisar a seleção amarela.

### Trabalhar com PDFs

Selecione ou abra um PDF e escolha leitura de texto, conversão para HTML, conversão para PNG ou abertura gráfica. O eazy cria os arquivos derivados conforme a opção escolhida.

### Registrar uma ideia

Pressione `Ctrl-N`, escreva no editor, use `Esc` para salvar e sair ou `Ctrl-S` para salvar e abrir outra nota. A nota editada será a primeira a ser aberta na próxima chamada do editor.

## 28. Conclusão

O eazy é uma ferramenta para quem precisa administrar arquivos multimídia e deseja um fluxo concentrado, rápido e persistente. Ele não se limita a reproduzir mídia: também pesquisa, organiza, converte, cria filas, gerencia playlists, registra histórico, encontra duplicados, baixa conteúdo, consulta o sistema, protege operações e mantém notas rápidas.

A combinação de seleção múltipla, diretórios tratados corretamente, listas temporárias nomeadas, pesquisas salvas, histórico, persistência do cursor, destinos lembrados, DRY-RUN e manutenção integrada torna o eazy especialmente útil para bibliotecas pessoais, diretórios de trabalho e coleções multimídia extensas.

---

**Projeto:** Easy_Player  
**Comando:** `eazy`  
**Arquivo:** `EAZY_EXPLICADO.md`
**Dados do usuário:** `~/.config/eazy/`

## Referências

[1]: https://github.com/vapesmadcat-blip/Easy_Player "Repositório oficial do Easy_Player"

O código-fonte e as versões publicadas estão disponíveis no [repositório oficial do projeto][1].
