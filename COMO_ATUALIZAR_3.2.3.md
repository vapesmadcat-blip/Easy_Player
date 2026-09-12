# Atualizar eazy 3.2.3 (recursos novos)

## Opção A — binário completo + install

```bash
chmod +x eazy
./eazy --install
```

## Opção B — inject no eazy já instalado

```bash
curl -fsSL -o inject-features-3.2.3.py \
  https://raw.githubusercontent.com/vapesmadcat-blip/Easy_Player/main/inject-features-3.2.3.py
cp "$(command -v eazy)" ./eazy
python3 inject-features-3.2.3.py ./eazy
./eazy --install
```

## Recursos aplicados

| Recurso | Onde |
|---------|------|
| Lixeira | F9 → Abrir lixeira |
| Exportar notas | F9 → Exportar notas |
| HTML / links | Enter → browser (`xdg-open`) |
| Prune seleção global | Após delete do disco |
| Extensões no filtro | Prompt (videos/audios/…) |
| Del | Só o item sob o cursor |
| Shift+Del | Local/global (amarelo nos dups) |

Documentação: [README.md](README.md) · [CHANGELOG.md](CHANGELOG.md) · [GUIA_RAPIDO.md](GUIA_RAPIDO.md)
