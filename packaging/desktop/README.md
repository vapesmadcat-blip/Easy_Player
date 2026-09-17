# Pacotes de integração de desktop

O pacote `eazy` base é compatível com GNOME, KDE Plasma e outros ambientes. Os
metapacotes opcionais apenas declaram as ferramentas recomendadas para cada
desktop e dependem da mesma versão do pacote base:

```bash
sudo apt install ./eazy_3.3.2_all.deb
sudo apt install ./eazy-gnome_3.3.2_all.deb   # GNOME
sudo apt install ./eazy-kde_3.3.2_all.deb     # KDE Plasma
```

Eles não instalam uma segunda cópia do executável e podem ser removidos sem
apagar `~/.config/eazy`.
