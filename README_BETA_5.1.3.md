# Eazy_beta 5.1.3

## Execução sem instalação

Descompacte numa pasta (por exemplo, `Easy Beta`) e execute `./run-beta.sh` ou `./eazy`. Não é preciso instalar o programa. Mantenha `eazy-index.py` ao lado de `eazy`.

## Histórico SQLite

O banco fica em `~/.config/eazy/eazy-index.sqlite3`; o arquivo original continua em `~/.config/eazy/history`. Na primeira entrada pelo Ctrl+G ou por Ctrl+P → Histórico, o Easy avisa, recria `history_items` lendo o arquivo original diretamente, preserva o arquivo e retorna à navegação. Pressione o atalho novamente para abrir o histórico; a contagem, os caminhos e os metadados passam então a vir do SQLite.

Se a tabela estiver corrompida, este comando cria backup do banco e remove somente as tabelas `history_items` e `history_state`, sem mexer no índice de arquivos nem no histórico original:

```bash
python3 -c 'import os,sqlite3; from pathlib import Path; from datetime import datetime; base=Path(os.environ.get("XDG_CONFIG_HOME",Path.home()/".config")); p=base/"eazy"/"eazy-index.sqlite3"; assert p.is_file(), f"Banco não encontrado: {p}"; b=p.with_name(p.name+".backup-"+datetime.now().strftime("%Y%m%d-%H%M%S")); src=sqlite3.connect(p); dst=sqlite3.connect(b); src.backup(dst); dst.close(); src.execute("DROP TABLE IF EXISTS history_items"); src.execute("DROP TABLE IF EXISTS history_state"); src.commit(); src.close(); print(f"Histórico SQL limpo. Backup: {b}"); print("Arquivo original preservado; abra o Easy Beta e pressione Ctrl+G ou Ctrl+P > Histórico para reconstruir.")'
```

O importador lê uma linha por entrada e não converte letras `N` em `0`. O teste verifica ordem e caminhos contendo `N`, `0`, espaços e caracteres acentuados.
