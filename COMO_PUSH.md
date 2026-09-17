# Push 3.2.12

```bash
cd ~/prj
unzip -o eazy-3.2.12-release.zip
cp -f eazy-3.2.12-release/* ~/prj/Easy_Player/
cp -rf eazy-3.2.12-release/packaging ~/prj/Easy_Player/
cd ~/prj/Easy_Player
chmod +x eazy install.sh eazy-notes-editor 2>/dev/null || true
./eazy --install
eazy --version
man eazy

git add -A
git commit -m "eazy 3.2.12: deb GNOME/KDE, man, legenda, deps --install, docs"
git push origin main
```
