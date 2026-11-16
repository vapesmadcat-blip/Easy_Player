# Eazy Beta 5.2.0

## Execução sem instalação

Descompacte em uma pasta e execute `./run-beta.sh` ou `./eazy`. Mantenha `eazy-index.py` e `migrate_eazy_lists.py` ao lado de `eazy`.

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

O Ctrl+P abre filas, listas SQL, histórico e duplicados. Insert adiciona a seleção a uma fila ou permite criar tabela/lista personalizada. Del remove itens somente da lista; Alt+D é a ação separada para apagar arquivos físicos, após confirmação.
