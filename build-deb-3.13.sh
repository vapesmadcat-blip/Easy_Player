#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
PKG_DIR="$ROOT_DIR/.build/eazy-3.13"
OUT="$ROOT_DIR/eazy_3.13_all.deb"

rm -rf "$PKG_DIR"
mkdir -p "$PKG_DIR/DEBIAN" \
  "$PKG_DIR/usr/bin" \
  "$PKG_DIR/usr/lib/eazy" \
  "$PKG_DIR/usr/share/applications" \
  "$PKG_DIR/usr/share/man/man1" \
  "$PKG_DIR/usr/share/doc/eazy"

install -m755 "$ROOT_DIR/bin/eazy-linux-x86_64" "$PKG_DIR/usr/bin/eazy"
install -m755 "$ROOT_DIR/bin/eazy-linux-x86_64" "$PKG_DIR/usr/lib/eazy/eazy"
install -m755 "$ROOT_DIR/eazy-notes-editor" "$PKG_DIR/usr/lib/eazy/eazy-notes-editor"
install -m644 "$ROOT_DIR/eazy.desktop" "$PKG_DIR/usr/share/applications/eazy.desktop"
install -m644 "$ROOT_DIR/eazy.1" "$PKG_DIR/usr/share/man/man1/eazy.1"
install -m644 "$ROOT_DIR/README.md" "$PKG_DIR/usr/share/doc/eazy/README.md"
install -m644 "$ROOT_DIR/CHANGELOG.md" "$PKG_DIR/usr/share/doc/eazy/CHANGELOG.md"
install -m644 "$ROOT_DIR/EAZY_EXPLICADO.md" "$PKG_DIR/usr/share/doc/eazy/EAZY_EXPLICADO.md"
install -m644 "$ROOT_DIR/GUIA_RAPIDO.md" "$PKG_DIR/usr/share/doc/eazy/GUIA_RAPIDO.md"

cat > "$PKG_DIR/DEBIAN/control" <<'CONTROL'
Package: eazy
Version: 3.13
Section: video
Priority: optional
Architecture: all
Maintainer: John B Kersting <vapesmadcat-blip@users.noreply.github.com>
Depends: bash, fzf, whiptail, gawk, findutils, sed, wget | curl, mpv | mplayer | vlc | ffmpeg
Recommends: xdg-utils
Suggests: yt-dlp, aria2, axel, chafa, ffmpeg, p7zip-full, rar, konsole, dolphin, kate, kio-extras, pciutils, alsa-utils, pulseaudio-utils, pipewire-pulse, lshw, smartmontools, dmidecode, inxi, usbutils, lm-sensors
Description: terminal media browser and player
 eazy is a keyboard-driven terminal media browser and player built around
 fzf and a command-line media player. Works on KDE Plasma, GNOME and others.
 .
 Installs the protected Linux binary, notes editor, KDE-compatible desktop
 launcher and man page. User data lives in ~/.config/eazy.
CONTROL

cat > "$PKG_DIR/DEBIAN/postinst" <<'POSTINST'
#!/bin/sh
set -e
command -v mandb >/dev/null 2>&1 && mandb -q 2>/dev/null || true
command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database -q /usr/share/applications 2>/dev/null || true
command -v kbuildsycoca6 >/dev/null 2>&1 && kbuildsycoca6 --noincremental 2>/dev/null || true
command -v kbuildsycoca5 >/dev/null 2>&1 && kbuildsycoca5 --noincremental 2>/dev/null || true
exit 0
POSTINST
chmod 755 "$PKG_DIR/DEBIAN/postinst"

dpkg-deb --build --root-owner-group "$PKG_DIR" "$OUT" >/dev/null
sha256sum "$OUT" > "$OUT.sha256"
dpkg-deb -f "$OUT" Package Version Architecture
printf 'Pacote criado: %s\n' "$OUT"
printf 'Checksum: %s\n' "$OUT.sha256"
