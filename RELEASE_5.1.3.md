# Easy Player 5.1.3

## Correção do histórico SQLite

O histórico não converte letras nem substitui `N` por `0`. A migração lê diretamente `~/.config/eazy/history`, uma entrada por linha, recria `history_items` e marca a migração somente após concluir. O arquivo original é mantido intacto.

Se a tabela de histórico atual estiver corrompida, remova apenas `history_items` e `history_state` do banco `~/.config/eazy/eazy-index.sqlite3` (faça cópia de segurança antes). Na primeira tentativa de abrir o Histórico com `Ctrl+G` ou pelo menu `Ctrl+P`, o Easy exibe um aviso, importa o arquivo original e retorna sem abrir a tela; pressione o atalho novamente. A contagem, a lista e os metadados subsequentes vêm do SQLite.

Para reconstruir no WSL com uma cópia de segurança automática do banco, use:

```bash
python3 -c 'import os,sqlite3; from pathlib import Path; from datetime import datetime; base=Path(os.environ.get("XDG_CONFIG_HOME",Path.home()/".config")); p=base/"eazy"/"eazy-index.sqlite3"; assert p.is_file(), f"Banco não encontrado: {p}"; b=p.with_name(p.name+".backup-"+datetime.now().strftime("%Y%m%d-%H%M%S")); src=sqlite3.connect(p); dst=sqlite3.connect(b); src.backup(dst); dst.close(); src.execute("DROP TABLE IF EXISTS history_items"); src.execute("DROP TABLE IF EXISTS history_state"); src.commit(); src.close(); print(f"Histórico SQL limpo. Backup: {b}"); print("Arquivo original preservado; abra o Easy Beta e pressione Ctrl+G ou Ctrl+P > Histórico para reconstruir.")'
```

Para uso beta sem instalação: descompacte, entre na pasta e rode `./run-beta.sh`. Depois do reset, abra Histórico; a primeira tentativa exibe a mensagem, migra e retorna, e a segunda tentativa abre a lista.

O auxiliar `eazy-index.py` acompanha o pacote em `/usr/lib/eazy/eazy-index.py`, e vai junto do executável nos arquivos ZIP/locales.

## Validação

O teste de regressão reconstrói a tabela em um banco temporário, compara conteúdo e ordem com o arquivo original, confirma que o arquivo e outras tabelas permanecem intactos e verifica os caminhos Ctrl+G/Ctrl+P. Nenhum banco do usuário foi alterado durante a construção desta release.
