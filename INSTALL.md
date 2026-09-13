# eazy 3.2.10 — instalar e atualizar o repo

Zip em `~/prj`, repo em `~/prj/Easy_Player`.

```bash
cd ~/prj
unzip -o eazy-3.2.10-release.zip
cp -f eazy-3.2.10-release/* ~/prj/Easy_Player/
cd ~/prj/Easy_Player
chmod +x eazy install.sh eazy-notes-editor 2>/dev/null || true
./eazy --install
eazy --version

git add eazy eazy-3.2.10 VERSION README.md CHANGELOG.md INSTALL.md \
        eazy.desktop install.sh eazy-notes-editor \
        eazy_3.2.10_all.deb eazy_3.2.10_all.deb.sha256 2>/dev/null || true
git add -A
git commit -m "eazy 3.2.10: Enter py/sh/html menu estilo PDF"
git push origin main
```
