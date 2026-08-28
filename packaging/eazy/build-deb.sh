#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
PROJECT_DIR="$(cd -- "$SCRIPT_DIR/../.." && pwd -P)"
SRC_DIR="$PROJECT_DIR"
DEBIAN_DIR="$SCRIPT_DIR/debian"
PKGROOT="$SCRIPT_DIR/pkgroot"
DIST_DIR="$SCRIPT_DIR/dist"
PACKAGE="eazy"
VERSION="3.0-44"
ARCH="all"
OUTPUT="$DIST_DIR/${PACKAGE}_${VERSION}_${ARCH}.deb"

for required in dpkg-deb install; do
    command -v "$required" >/dev/null 2>&1 || {
        printf 'Erro: comando necessário não encontrado: %s\n' "$required" >&2
        exit 1
    }
done

for required_file in "$SRC_DIR/eazy" "$SRC_DIR/eazy-notes-editor" "$SRC_DIR/eazy.desktop" "$SRC_DIR/README.md" "$SRC_DIR/CHANGELOG.md" "$SRC_DIR/EAZY_EXPLICADO.md" "$DEBIAN_DIR/control" "$DEBIAN_DIR/changelog" "$DEBIAN_DIR/copyright"; do
    [ -f "$required_file" ] || {
        printf 'Erro: arquivo necessário não encontrado: %s\n' "$required_file" >&2
        exit 1
    }
done

rm -rf "$PKGROOT"
mkdir -p "$DIST_DIR"
mkdir -p \
    "$PKGROOT/DEBIAN" \
    "$PKGROOT/usr/bin" \
    "$PKGROOT/usr/lib/eazy" \
    "$PKGROOT/usr/share/applications" \
    "$PKGROOT/usr/share/doc/$PACKAGE"

install -m 0755 "$SRC_DIR/eazy" "$PKGROOT/usr/bin/eazy"
install -m 0755 "$SRC_DIR/eazy-notes-editor" "$PKGROOT/usr/lib/eazy/eazy-notes-editor"
install -m 0644 "$SRC_DIR/eazy.desktop" "$PKGROOT/usr/share/applications/eazy.desktop"
install -m 0644 "$SRC_DIR/README.md" "$PKGROOT/usr/share/doc/$PACKAGE/README.md"
install -m 0644 "$SRC_DIR/CHANGELOG.md" "$PKGROOT/usr/share/doc/$PACKAGE/CHANGELOG.md"
install -m 0644 "$SRC_DIR/EAZY_EXPLICADO.md" "$PKGROOT/usr/share/doc/$PACKAGE/EAZY_EXPLICADO.md"
install -m 0644 "$DEBIAN_DIR/control" "$PKGROOT/DEBIAN/control"
install -m 0644 "$DEBIAN_DIR/changelog" "$PKGROOT/usr/share/doc/$PACKAGE/changelog.Debian"
install -m 0644 "$DEBIAN_DIR/copyright" "$PKGROOT/usr/share/doc/$PACKAGE/copyright"

gzip -n -9 -f "$PKGROOT/usr/share/doc/$PACKAGE/changelog.Debian"

touch "$PKGROOT/DEBIAN/conffiles"

dpkg-deb --build --root-owner-group "$PKGROOT" "$OUTPUT" >/dev/null

printf 'Pacote criado: %s\n' "$OUTPUT"
printf 'Tamanho: '
du -h "$OUTPUT" | cut -f1
printf '\nMetadados:\n'
dpkg-deb --info "$OUTPUT" | sed -n '1,18p'
printf '\nConteúdo:\n'
dpkg-deb --contents "$OUTPUT"
