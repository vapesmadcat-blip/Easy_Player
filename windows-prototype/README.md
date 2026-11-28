# Protótipo Easy para Windows

Esta pasta contém uma prova de conceito isolada da edição nativa para Windows. Ela demonstra navegação por teclado com caminhos locais ou UNC, seleção amarela limitada ao diretório atual e o menu Ctrl+K com prioridade para a seleção local. Quando não há amarelos, Ctrl+K usa apenas o arquivo sob o cursor; ações de demonstração sem arquivo continuam acessíveis.

## Executar no Windows

Requer Python 3, sem bibliotecas extras. Abra o Windows Terminal ou PowerShell na pasta e execute:

```powershell
py -3 .\eazy-win-demo.py "$env:USERPROFILE"
```

Sem argumento, começa na pasta atual. Para testar uma pasta de rede, pode-se passar o caminho UNC entre aspas, por exemplo `\\servidor\compartilhamento\pasta`.

Teclas: setas para mover, Enter para abrir diretórios ou abrir arquivos pelo aplicativo padrão, Backspace para voltar, Espaço para marcar/desmarcar amarelo, Ctrl+K para o menu de ações e `Q` para sair. No Ctrl+K, `1` mostra um resumo dos alvos e `M` demonstra uma ação sem alvo de arquivo.

## Limites desta amostra

É um protótipo de interface, não uma versão completa do Easy. Não grava no SQLite de produção, não apaga, copia ou move arquivos, não implementa indexação, watcher, mídia, playlists ou configurações. A seleção existe apenas na memória desta execução. O código usa APIs de diretório do Python executado no próprio Windows, sem converter caminhos para `/mnt/c` e sem chamar `find` ou um shell Unix.

O arquivo inclui um teste simples de enumeração e metadados:

```powershell
py -3 .\eazy-win-demo.py --self-test
```

O self-test foi executado no ambiente Linux de desenvolvimento. Ainda é necessário executar a amostra em Windows real para validar o teclado e o console Windows antes de usá-la como base de um porte maior.
