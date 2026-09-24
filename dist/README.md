# dist/ — eazy 4.2.1 (fora de Releases)

Coloque aqui (via `git push` ou upload na UI do GitHub):

- `eazy_4.2.1_all.deb`
- `eazy_4.2.1_full.zip`

Depois o install funciona:

```bash
curl -fsSL https://raw.githubusercontent.com/vapesmadcat-blip/Easy_Player/main/install-from-web.sh | bash
```

## Enviar o deb a partir do zip local

```bash
unzip eazy_4.2.1_full.zip
cd eazy-4.2.1-full
git clone https://github.com/vapesmadcat-blip/Easy_Player.git
cd Easy_Player
mkdir -p dist
cp ../eazy_4.2.1_all.deb ../eazy_4.2.1_full.zip dist/
git add dist/
git commit -m "dist: eazy 4.2.1 deb + zip"
git push origin main
```
