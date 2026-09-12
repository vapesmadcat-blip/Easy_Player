# Instalação em ~/prj/Easy_Player
```bash
cd ~/prj/Easy_Player
unzip -o eazy-3.2.5-release.zip
cp -f eazy-3.2.5-release/* .
chmod +x eazy install.sh eazy-notes-editor
./eazy --install
eazy --shell-init >> ~/.bashrc && source ~/.bashrc
git add -A && git commit -m "eazy 3.2.5" && git push
```
