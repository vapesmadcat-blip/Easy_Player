# Guia rápido do eazy

## Iniciar

Execute `eazy` para abrir o navegador. Use `Enter` para entrar em pastas ou abrir arquivos, `Tab` para selecionar e avançar, `Espaço` para selecionar sem avançar e `Esc` para cancelar uma operação interrompível.

## Pesquisa por nome e extensão

Pressione `Ctrl-F`. O campo aceita vários padrões separados por espaço ou vírgula:

```text
sh mp4 vid* filme.mov movie.*
```

A interpretação é a seguinte:

| Padrão | Significado |
|---|---|
| `sh` | Arquivos com extensão `.sh` |
| `mp4` | Arquivos com extensão `.mp4` |
| `vid*` | Nomes que começam com `vid` |
| `filme.mov` | Nome específico `filme.mov` |
| `movie.*` | Nomes que começam com `movie.` e qualquer extensão |

## Busca por conteúdo

Na etapa de conteúdo, escolha **Sim — digitar uma ou mais palavras-chave**. A busca não diferencia maiúsculas de minúsculas e é aplicada somente depois do filtro por nome/extensão.

Palavras separadas por espaço significam `AND`:

```text
alpha beta
```

O arquivo precisa conter `alpha` e `beta`.

O operador `OR` aceita alternativas:

```text
alpha OR beta
```

O arquivo precisa conter pelo menos um dos termos.

O operador `NOT` exclui arquivos:

```text
alpha AND NOT debug
```

O arquivo precisa conter `alpha` e não pode conter `debug`.

Frases entre aspas preservam os espaços:

```text
"erro grave" AND NOT debug
```

Essa expressão exige a frase literal `erro grave` e rejeita arquivos que contenham `debug`. Uma frase pode ser combinada com alternativas:

```text
"falha crítica" OR timeout
```

Operadores dentro de aspas são texto literal:

```text
"AND"
```

## Combinações práticas

Para localizar scripts que contenham uma frase, use:

```text
Padrão: sh
Conteúdo: "backup concluído" AND NOT teste
```

Para localizar vídeos com uma das duas palavras, use:

```text
Padrão: vid* mp4
Conteúdo: música OR entrevista
```

Para localizar relatórios que tenham duas palavras e não estejam marcados como rascunho, use:

```text
Padrão: relatorio.*
Conteúdo: cliente AND pagamento AND NOT rascunho
```

## Pesquisas salvas

Salve a pesquisa com um nome quando quiser reutilizá-la. O eazy guarda os parâmetros e o snapshot dos resultados. Ao abrir novamente, o snapshot é mostrado sem refazer a busca. Pressione `Alt-R` dentro da lista para solicitar um remake.

## Manutenção e DRY-RUN

Use `eazy -m` para a manutenção normal ou `eazy -a` para a manutenção avançada. A limpeza seletiva permite escolher playlists, listas, pesquisas, notas, histórico, downloads, cache, estado e backups. O modo **DRY-RUN** mostra o que seria feito, calcula o espaço estimado e não remove dados.

Nas limpezas, a tela é limpa antes do comando, o resultado fica visível depois da execução e o eazy aguarda confirmação para retornar ao menu. Antes de qualquer remoção real, revise a prévia e a confirmação.

## Seleção persistente e filas

A seleção normal é persistente por caminho completo. Ela não é apagada quando você entra em um diretório, executa um arquivo, volta por `..` ou muda de lista. Ao entrar em uma pasta que foi selecionada, os arquivos marcados daquela pasta reaparecem marcados.

| Tecla | Ação |
|---|---|
| `Espaço` ou `Tab` | Marca/desmarca o item sob o cursor. Em um diretório, marca/desmarca recursivamente todos os arquivos dele. |
| `Ctrl-A` | Marca os itens visíveis da lista atual; não faz seleção recursiva. |
| `Enter` | Executa somente o item sob o cursor, ignorando a seleção global. Em um diretório, entra nele e preserva as seleções anteriores. |
| `Alt+Enter` | Executa todos os arquivos atualmente marcados na seleção global. |
| `Ctrl-X` | Zera somente a seleção local do diretório atual. |
| `Alt-X` | Pergunta e, após confirmação, zera toda a seleção global. |
| `Home` | Vai ao primeiro item da lista. |
| `End` | Vai ao último item da lista. |

A seleção é armazenada por caminho absoluto em `~/.config/eazy/selected_paths`, evitando que a posição visual de um arquivo em outra pasta seja confundida com a seleção real. Use `Insert` para enviar itens às filas 1, 2 ou 3 e `Ctrl-P` para alternar entre filas e pasta.

Exemplo: se três arquivos e três diretórios estiverem marcados, `Enter` sobre um diretório apenas entra nele e preserva as seis marcações. Dentro dele, marque mais dois arquivos e pressione `Enter` sobre `..`; ao voltar, todas as marcações continuam ativas. Para executar tudo, use `Alt+Enter`.

O guia completo está em [`EAZY_EXPLICADO.md`](EAZY_EXPLICADO.md).
