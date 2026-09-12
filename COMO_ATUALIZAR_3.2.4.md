# eazy 3.2.4 — atualizar e publicar

## No teu PC (commit + push)

```bash
cd Easy_Player
# extrai o zip nesta pasta ou copia os ficheiros
cp /caminho/eazy-3.2.4-release/eazy .
cp /caminho/eazy-3.2.4-release/VERSION .
cp /caminho/eazy-3.2.4-release/README.md .
cp /caminho/eazy-3.2.4-release/CHANGELOG.md .
cp /caminho/eazy-3.2.4-release/GUIA_RAPIDO.md .
cp /caminho/eazy-3.2.4-release/eazy.desktop .
chmod +x eazy

git add eazy VERSION README.md CHANGELOG.md GUIA_RAPIDO.md eazy.desktop COMO_ATUALIZAR_3.2.4.md
git commit -m "eazy 3.2.4: HTML/URL no browser, revisão no cabeçalho, docs"
git push origin main

# Release (opcional)
gh release create eazy-v3.2.4 eazy \
  --title "eazy 3.2.4" \
  --notes "HTML/URL abrem no browser. Ver CHANGELOG.md."
```

## Instalar localmente

```bash
chmod +x eazy
./eazy --install
eazy --version
```
