# eazy 3.2.12 — descompactar e push

```bash
cd ~/prj   # ou pasta do seu clone
unzip -o eazy-3.2.12-release.zip
cp -f eazy-3.2.12-release/* ~/prj/Easy_Player/ 2>/dev/null || true
# se a pasta packaging existir:
cp -rf eazy-3.2.12-release/packaging ~/prj/Easy_Player/ 2>/dev/null || true
cd ~/prj/Easy_Player
chmod +x eazy install.sh eazy-notes-editor packaging/eazy/build-deb.sh 2>/dev/null || true

git add eazy eazy.1 eazy-notes-editor eazy.desktop VERSION README.md CHANGELOG.md \
        EAZY_EXPLICADO.md GUIA_RAPIDO.md INSTALL.md \
        eazy_3.2.12_all.deb eazy_3.2.12_all.deb.sha256 packaging 2>/dev/null || true
git add -A
git commit -m "eazy 3.2.12: man completa, deb KDE, cache, sel global, downloads editáveis"
git push origin main
```

Conferir:
```bash
./eazy --version
sudo dpkg -i eazy_3.2.12_all.deb
man eazy
```
