# Easy Player 5.2.0

## Persistência local SQLite

As filas temporárias 1, 2 e 3 e as listas personalizadas agora têm tabelas SQLite próprias no banco local `~/.config/eazy/eazy-index.sqlite3`. O menu Ctrl+P, a criação, inclusão, remoção, manutenção e reprodução consultam as tabelas; não dependem de arquivos de lista permanentes. Os snapshots em `~/.config/eazy/tmp/` são transitórios e servem somente à compatibilidade interna.

A distribuição inclui `migrate_eazy_lists.py` para converter os arquivos legados. Feche o Easy, examine a prévia com `python3 migrate_eazy_lists.py` e execute `python3 migrate_eazy_lists.py --apply` para aplicar. O processo preserva os arquivos originais e faz backup do banco antes de gravar. O Easy não importa arquivos antigos silenciosamente.

## Performance e manutenção

As listas carregam metadados por consulta em lote, evitando subprocessos por título. A manutenção valida e corrige referências diretamente nas tabelas SQLite. A sincronização de diretórios atualiza o índice incrementalmente quando há alterações. Arquivos normais seguem identificados por nome, tamanho e data de modificação; CRC continua restrito ao fluxo de verificação de duplicados.

## Histórico

Mantém a reconstrução segura do histórico SQLite da versão 5.1.3: leitura linha a linha do arquivo original, preservação da origem e guardas comuns para Ctrl+G e Ctrl+P.

## Validação

A bateria `python3 -m unittest discover -s tests -p 'test_sqlite_*.py' -v` cobre fonte SQLite, lookup em lote, manutenção, integridade, CRUD de listas e preservação dos arquivos legados. A sintaxe do Bash e os metadados dos pacotes são verificados durante a geração dos artefatos.
