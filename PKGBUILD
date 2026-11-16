# Maintainer: eazy packagers
pkgname=eazy
pkgver=5.2.0
pkgrel=1
pkgdesc="Terminal multimedia browser and player with SQLite lists/history"
arch=('any')
url="https://github.com/vapesmadcat-blip/Easy_Player"
license=('custom:freeware')
depends=('bash' 'python' 'fzf' 'libnewt' 'findutils' 'gawk' 'sed')
optdepends=(
  'mpv: recommended player'
  'yt-dlp: online video downloads'
  'aria2: download accelerator'
  'ffmpeg: ffplay and conversions'
  'eazy-tor: magnet and torrent support'
)
source=("https://github.com/vapesmadcat-blip/Easy_Player/archive/refs/tags/v${pkgver}.tar.gz")
sha256sums=('SKIP')

prepare() {
  cd "${srcdir}"
  local archive_dir="Easy_Player-${pkgver}"
  if [[ -d "$archive_dir" ]]; then
    mv "$archive_dir" "eazy-${pkgver}"
  fi
}

package() {
  cd "${srcdir}/eazy-${pkgver}"
  install -Dm755 eazy "${pkgdir}/usr/bin/eazy"
  install -Dm644 eazy-index.py "${pkgdir}/usr/lib/eazy/eazy-index.py"
  install -Dm755 migrate_eazy_lists.py "${pkgdir}/usr/lib/eazy/migrate_eazy_lists.py"
  for companion in eazy-yt-stream eazy-tor eazy-ai.py eazy-notes-editor; do
    install -Dm755 "$companion" "${pkgdir}/usr/lib/eazy/$companion"
  done
  install -Dm644 eazy.desktop "${pkgdir}/usr/share/applications/eazy.desktop"
  install -Dm644 eazy.1 "${pkgdir}/usr/share/man/man1/eazy.1"
  install -Dm644 README.md "${pkgdir}/usr/share/doc/${pkgname}/README.md"
  install -Dm644 CHANGELOG.md "${pkgdir}/usr/share/doc/${pkgname}/CHANGELOG.md"
  install -Dm644 docs/eazy-help-5.2.0.txt "${pkgdir}/usr/share/doc/${pkgname}/eazy-help.txt"
  install -Dm644 docs/eazy-help-5.2.0.html "${pkgdir}/usr/share/doc/${pkgname}/eazy-help.html"
}
