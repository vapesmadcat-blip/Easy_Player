# eazy 3.2.4

## O que mudou

- **Enter** em `.html` / `.htm` / URL abre o **browser** (`xdg-open` com `file://` absoluto, fallbacks: gio, firefox, chromium…)
- Cabeçalho do script com **Revisão 3.2.4**
- Mantidos: Del/Shift+Del, lixeira, prune seleção, filtros com extensões, export notas

## Instalar

```bash
chmod +x eazy
./eazy --install
eazy --version   # eazy 3.2.4 (release)
```

## Testar HTML

```bash
echo '<h1>ok</h1>' > /tmp/teste.html
eazy /tmp
# Enter em teste.html → deve abrir o browser
```
