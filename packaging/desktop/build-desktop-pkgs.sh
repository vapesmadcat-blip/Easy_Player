#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd -P)"
VERSION="${1:-3.3.2}"
DIST="$ROOT/packaging/desktop/dist"
rm -rf "$ROOT/packaging/desktop/pkgroot-gnome" "$ROOT/packaging/desktop/pkgroot-kde"
mkdir -p "$DIST"
make_meta() {
  local flavor="$1"; shift
  local root="$ROOT/packaging/desktop/pkgroot-$flavor"
  local pkg="eazy-$flavor"
  local recommends
  recommends="$(printf '%s, ' "$@" | sed 's/, $//')"
  mkdir -p "$root/DEBIAN" "$root/usr/share/doc/$pkg"
  cat > "$root/DEBIAN/control" <<CONTROL
Package: $pkg
Version: $VERSION
Section: video
Priority: optional
Architecture: all
Maintainer: eazy contributors <vapesmadcat-blip@users.noreply.github.com>
Depends: eazy (= $VERSION)
Recommends: $recommends
Description: eazy desktop integration for ${flavor^}
 Meta-package for eazy with recommended ${flavor^} terminal, file manager and
 desktop utilities. The eazy executable is provided by the base eazy package.
CONTROL
  printf 'eazy desktop integration %s\n' "$VERSION" > "$root/usr/share/doc/$pkg/README"
  dpkg-deb --build --root-owner-group "$root" "$DIST/${pkg}_${VERSION}_all.deb" >/dev/null
}
make_meta gnome gnome-terminal nautilus gedit evince xdg-utils
make_meta kde konsole dolphin kate kio-extras xdg-utils
printf 'Pacotes criados em %s\n' "$DIST"
