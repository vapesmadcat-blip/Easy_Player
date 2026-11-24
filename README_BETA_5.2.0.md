# Eazy 5.2.0 — rev.51 beta

## Execução sem instalação

Descompacte em uma pasta e execute `./run-beta.sh` ou `./eazy`. Mantenha `eazy-index.py`, `migrate_eazy_lists.py` e `eazy-convert-m3u.py` ao lado de `eazy`.

## Edição Windows (preview)

No Windows, execute `py eazy-win.py` (Python 3 necessário), mantendo `eazy-convert-m3u.py` na mesma pasta. Esta edição inicial, baseada no protótipo recebido, oferece navegação local, seleção amarela, abertura padrão de arquivos e um menu ao pressionar Enter em `.m3u`/`.m3u8` para abrir/reproduzir, converter ou cancelar.

Em **F9 → Integração**, configure o destino Windows (por padrão `%USERPROFILE%\\EazyData`), o destino Linux/WSL como caminho UNC acessível pelo Windows (por exemplo, `\\\\wsl.localhost\\Ubuntu\\home\\USUARIO\\EazyData`) e o nome da distribuição WSL. A tela também consulta volumes montados e sistemas de arquivos do Windows. A conversão chama o mesmo `eazy-convert-m3u.py` da edição Linux/WSL, envia o resultado à pasta do sistema de destino e preserva a playlist original.

**Escopo:** a edição Windows continua sendo um preview separado; ainda não tem paridade com o Eazy Linux/WSL, não usa o banco SQLite de produção e não implementa as operações completas de arquivos. A experiência interativa e a leitura de sistemas de arquivos devem ser validadas em um Windows real; o self-test no Linux cobre somente lógica portátil.

## Migração de filas e listas antigas

Feche todas as instâncias do Easy. Confira primeiro a prévia:

```bash
python3 migrate_eazy_lists.py
```

Aplique somente depois de revisar:

```bash
python3 migrate_eazy_lists.py --apply
```

O banco padrão é `~/.config/eazy/eazy-index.sqlite3`. O migrador faz backup do banco anterior e preserva os arquivos antigos. Filas e listas personalizadas são tabelas SQLite; os snapshots de texto em `~/.config/eazy/tmp/` são transitórios e não constituem armazenamento permanente.

## Histórico

A migração do histórico lê diretamente `~/.config/eazy/history`, linha a linha, recria `history_items` e mantém o arquivo original intacto. Na primeira tentativa de abrir Histórico pelo Ctrl+G ou Ctrl+P, o Easy migra e retorna; entre novamente para consultar os dados SQLite.

## Operações

Ao pressionar Enter em um arquivo `.m3u` ou `.m3u8`, o Eazy pergunta se deseja navegar na playlist, reproduzi-la imediatamente, converter automaticamente os caminhos entre Linux/WSL e Windows ou cancelar. A conversão preserva o original e escolhe um nome livre se já existir uma conversão anterior.

Em **F9 → Integração**, configure o diretório Windows acessível pelo WSL (por exemplo, `/mnt/c/Users/USUARIO/EazyData`) e o diretório Linux de saída (por exemplo, `$HOME/EazyData`). A opção de montagens exibe os pontos detectados e o tipo de sistema de arquivos (`drvfs`/NTFS, `9p`, `ext4` e outros). Caminhos Linux convertidos para Windows são gravados no destino Windows; caminhos Windows convertidos para Linux são gravados no destino Linux. O Easy pergunta antes de criar uma pasta de destino que ainda não exista.

O Ctrl+P abre filas, listas SQL, Última pesquisa, Seleção global, histórico e duplicados. A opção **Seleção global** mostra os caminhos selecionados entre pastas; **Del** remove itens da seleção global sem apagar arquivos do disco. Insert adiciona a seleção atual a uma fila ou permite criar tabela/lista personalizada. Alt+D é a ação separada para apagar arquivos físicos, após confirmação.

As marcas de seleção usam a coluna `selected` do índice SQLite: `0` = desmarcado, `1` = imediato/local e `2` = global/persistente. Espaço/Tab alternam a marca local; Ctrl+A e Ctrl+R alteram em lote os itens visíveis diretamente no banco; ao sair da listagem para navegação ou outras ações, marcas `1` são promovidas para `2` em lote. **Ctrl+Y/Ctrl+U e copiar/mover pelo Ctrl+K são exceções:** preservam o estado amarelo durante a decisão e, se houver estado global, perguntam se deve ser incluído. O antigo arquivo `selected_paths` não é mais importado nesta revisão; a seleção anterior pode ser descartada.

Na cópia de árvores, o Easy simula espaço e conflitos antes de escrever. Para cada conflito, renomear, sobrescrever, pular e continuar, pular os restantes ou cancelar são decisões tomadas nesta etapa; após a confirmação final, a cópia real não abre menus de conflito. Se o destino mudar inesperadamente depois da simulação, a operação para por segurança em vez de interromper o usuário com uma nova pergunta.

No modo **Duplicados**, Tab/Espaço, Ctrl+A, Ctrl+R, Ctrl+X, Ctrl+T e F12 também usam a tabela SQLite `eazy_duplicate_marks`, separada por sessão. A amostra fixa vermelha do F12 fica distinta da seleção ativa amarela; os arquivos temporários restantes são apenas snapshots de exibição/compatibilidade.

O **Alt+X** mostra a contagem, soma dos tamanhos (`SUM(size)`) e quantidade de pastas da seleção global por uma consulta agregada no SQLite. Não percorre os caminhos nem executa `stat`/`du` por item antes de limpar.

Tab/Espaço/Shift+Tab agora fazem apenas o toggle necessário no SQLite e o marcador de seleção do fzf; não chamam `eazy_ensure_selection`, não gravam os snapshots de texto, nem recalculam o cabeçalho completo (que consultava o disco e reabria dados de seleção). Ctrl+R também deixou de recompor esse cabeçalho. Ctrl+A e Ctrl+X atualizam o snapshot somente no reload visual. Snapshots locais são atualizados apenas quando a lista é redesenhada e os arquivos auxiliares só são substituídos se o conteúdo mudou.

No modo **Pesquisa**, Ctrl+A marca no SQLite os resultados visíveis e atualiza o snapshot global para que o reload mostre a marca em resultados encontrados dentro de subpastas, não apenas nos itens diretamente sob a pasta de origem.

No filtro da lista, digitar `.` mostra arquivos sem extensão (mantendo diretórios navegáveis); digitar `#` mostra apenas os itens selecionados na pasta atual, tanto seleção local quanto global. `# termo` limita os selecionados ao termo adicional.

Ctrl+A alterna todos os resultados visíveis como seleção imediata (`selected=1`); uma segunda pressão, se todos estiverem selecionados, limpa as marcas (`selected=0`). Estados globais existentes são removidos quando o lote visível já está inteiramente marcado. A marcação fzf acompanha o resultado (seleciona tudo ou limpa tudo). A promoção para global (`selected=2`) ocorre ao sair da pasta ou iniciar outras ações, não no Ctrl+A nem antes da escolha de escopo de copiar/mover.

Correção visual adicional: Ctrl+A não recarrega a listagem após alterar a seleção. O transform aplica `select-all` ou `deselect-all` diretamente na lista corrente, evitando que um reload assíncrono limpe os marcadores recém-aplicados.

Histórico: ao reproduzir um arquivo, a inclusão é gravada pela operação transacional SQLite `history-record`; Del na tela do Histórico remove somente aquela linha de `history_items`. O callback de foco entrega a linha atual ao handler mesmo sem pressionar Enter. O arquivo físico permanece intacto e erros SQL são enviados ao log da sessão.

Inicialização: o cabeçalho usa uma única consulta agregada para as estatísticas global e local da seleção. Removido o cálculo de tamanho por item (`stat`/`du`) e a consulta SQL local duplicada antes da primeira lista; a vista ainda consulta as marcas da pasta atual quando precisa renderizar os indicadores.

Na abertura, filas SQL não são mais exportadas por inteiro nem todas as listas personalizadas enumeradas para arquivos temporários. Esses dados são carregados sob demanda ao abrir uma lista. A sincronização do diretório atual compara agregados (quantidade de arquivos, bytes e diretórios) com o banco e só percorre as linhas do índice para atualizar quando os totais mudam; não calcula CRC.


## Teste local — HTML de Ctrl+H

Cada arquivo ou imagem exportado agora tem o botão **Ir para a pasta**, incluindo os modos tabela/árvore, galeria de imagens e galeria de conteúdo misto. O botão aponta para a pasta do item por um link `file://` convertido para WSL/Windows; o comportamento final depende do navegador e das permissões locais.

Uma página HTML estática não pode abrir diretamente o seletor nativo **Abrir com** nem executar comandos do sistema; isso exigiria um auxiliar/protocolo instalado no sistema. Os links existentes para abrir arquivos continuam disponíveis.


## Lista “Última pesquisa”

No modo normal (não `--ignore`), depois que uma nova busca termina (ou é interrompida e os resultados parciais são aceitos), seus caminhos são gravados na tabela interna `eazy_internal_last_search` do SQLite local — tanto na consulta rápida pelo índice SQLite quanto na varredura tradicional. A lista aparece no **Ctrl+P** como **Última pesquisa**; é possível reabri-la depois de sair da busca ou reiniciar o Easy. A próxima busca substitui os itens da lista. Nenhum arquivo permanente de lista é criado. O modo anônimo `--ignore` não persiste a busca.

## Notes editor

O pacote usa a versão do `eazy-notes-editor` fornecida pelo usuário, preservando seus atalhos Ctrl+C/Ctrl+V. A moldura é estática; as setas movem apenas o cursor visível; ao digitar, somente o sufixo alterado da linha é escrito. O ZIP inclui o `eazy-index.py` correspondente, necessário para gravar e exibir Última pesquisa em SQLite. A tela não é limpa por tecla. Teste diretamente e pelo atalho **Ctrl+N** no Easy.


## Revisão de teste 26 — Duplicados em SQLite

A lista persistente de resultados da busca de duplicados agora fica na tabela dedicada `eazy_duplicate_results` do SQLite, preservando a ordem e os campos hash, tamanho e caminho. O antigo `temp_duplicados` é lido apenas uma vez, na primeira inicialização da tabela; depois disso, abrir, contar, substituir, remover itens, limpar, fazer backup/restauração, validar e exportar HTML consulta o SQLite. Arquivos TSV restantes são materializações temporárias para a interface FZF/exportação, não fonte de persistência. O modo `--ignore` usa banco temporário isolado.

A tabela de resultados é separada de `eazy_duplicate_marks`, que continua isolada por sessão. **F12** marca em vermelho um arquivo de cada grupo de conteúdo duplicado; **Ctrl+T** copia todos esses marcados para amarelo (seleção ativa). Tab/Espaço, Ctrl+A, Ctrl+R e Ctrl+X continuam atuando na seleção amarela sem alterar as marcas vermelhas.


## Revisão de teste 27 — totais e marcas em tempo real

Os atalhos que alteram seleção agora atualizam o texto do cabeçalho sem recarregar a lista. No navegador normal, o total local usa o agregado SQL e reflete os bytes assim que Espaço/Tab, Ctrl+A, Ctrl+R ou Ctrl+X altera a seleção. Em Duplicados, F12 sincroniza imediatamente o snapshot vermelho; Ctrl+T continua copiando as marcas vermelhas para a seleção amarela. A soma da seleção amarela de Duplicados passa a usar os tamanhos guardados em `eazy_duplicate_results`, sem depender de os caminhos também estarem presentes em `files`. Fora do modo Duplicados, Ctrl+T continua sendo tratado pelo fluxo normal (ordenação por horário de acesso).


## Revisão de teste 28 — caminho do item focado

A navegação mostra o caminho completo do item sob o cursor na parte inferior da caixa. O caminho é extraído do último campo da linha da lista e mantém espaços corretamente; links são exibidos sem conversão para caminho local. Em FZF 0.63 ou posterior usa-se o rodapé dinâmico atualizado no evento `focus`. Em versões anteriores, o Easy detecta a falta de `--footer` e usa uma faixa inferior de preview com uma linha, sem substituir o preview detalhado quando este está ativado.


## Revisão de teste 29 — marcas independentes em Duplicados

F12 grava em vermelho o primeiro item existente de cada grupo de conteúdo duplicado. Ctrl+T copia as marcas vermelhas para a seleção amarela. Espaço alterna somente o amarelo do item focado e redesenha a linha a partir dos estados SQL; a marca vermelha fixa permanece inalterada. Quando o primeiro caminho do grupo já não existe, F12 escolhe o primeiro caminho restante existente.
