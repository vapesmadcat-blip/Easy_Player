# Maintainer: eazy packagers
pkgname=eazy
pkgver=3.2
pkgrel=1
pkgdesc="Terminal multimedia browser and player (fzf + mpv)"
arch=('any')
url="https://github.com/vapesmadcat-blip/Easy_Player"
license=('custom:freeware')
depends=('bash' 'fzf' 'libnewt' 'findutils' 'gawk')
optdepends=(
  'mpv: recommended player'
  'yt-dlp: online video downloads'
  'aria2: download accelerator'
  'ffmpeg: ffplay and conversions'
)
source=("https://github.com/vapesmadcat-blip/Easy_Player/archive/refs/heads/main.tar.gz")
sha256sums=('SKIP')

prepare() {
  cd "${srcdir}"
  # archive may unpack as Easy_Player-main
  if [ -d Easy_Player-main ]; then
    rm -rf "eazy-${pkgver}"
    mv Easy_Player-main "eazy-${pkgver}"
  fi
}

package() {
  cd "${srcdir}/eazy-${pkgver}"
  install -Dm755 eazy "${pkgdir}/usr/bin/eazy"
  install -Dm644 README.md "${pkgdir}/usr/share/doc/${pkgname}/README.md"
}
