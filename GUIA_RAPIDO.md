# Guia rápido do eazy

## Iniciar

Execute `eazy` para abrir o navegador. Use `Enter` para executar somente o item sob o cursor, `Tab` para alternar o arquivo atual na seleção global e avançar, `Espaço` para alternar sem avançar e `Esc` para cancelar uma operação interrompível. Para executar o conjunto acumulado entre pastas, use `Alt-Enter`.

No navegador normal, `Ctrl-A`, `Ctrl-R` e `Ctrl-X` operam somente nos arquivos diretamente da pasta atual; `Alt-X` limpa toda a seleção global depois de uma confirmação textual `S/N`. A linha `..` e as subpastas nunca entram na seleção global.

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

Use `eazy -m

eazy -a` ou abra a manutenção pelo menu `Ctrl-K`. A limpeza seletiva permite escolher playlists, listas, pesquisas, notas, histórico, downloads, cache, estado e backups. O modo **DRY-RUN** mostra o que seria feito, calcula o espaço estimado e não remove dados.

Nas limpezas, a tela é limpa antes do comando, o resultado fica visível depois da execução e o eazy aguarda confirmação para retornar ao menu. Antes de qualquer remoção real, revise a prévia e a confirmação.

## Seleção e filas

Use `Insert` para enviar itens às filas 1, 2 ou 3. `Ctrl-P` alterna entre as filas e a pasta. No navegador normal, `Tab` alterna o arquivo na seleção global e avança; `Espaço` alterna o arquivo mantendo o cursor no mesmo lugar. `Enter` executa só o cursor, enquanto `Alt-Enter` executa todos os arquivos acumulados, inclusive os escolhidos em outras pastas.

O guia completo está em [`EAZY_EXPLICADO.md`](EAZY_EXPLICADO.md).
