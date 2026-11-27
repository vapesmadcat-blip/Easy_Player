PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin
VERSION = 5.2.0
REVISION = 56
BIN_DIR = bin
BIN_TARGET = $(BIN_DIR)/eazy-linux-x86_64
DIST_FILES = eazy eazy-win.py eazy-index.py eazy-convert-m3u.py eazy-live-watch.py full.c eazy-yt-stream eazy-tor eazy-ai.py eazy-notes-editor eazy.desktop eazy.1 README.md README_BETA_5.2.0.md RELEASE_5.2.0.md CHANGELOG.md EAZY_EXPLICADO.md GUIA_RAPIDO.md VERSION Makefile run-beta.sh install-eazy-pronto.sh install-from-web.sh install.sh uninstall.sh migrate_eazy_lists.py PKGBUILD packaging/build-deb.sh packaging/eazy/build-deb.sh packaging/eazy/debian/control packaging/eazy/debian/changelog packaging/eazy/debian/copyright docs/eazy-help-5.2.0.txt docs/eazy-help-5.2.0.html tests
DIST_STEM = eazy-$(VERSION)-rev$(REVISION)

.PHONY: install uninstall install-full compile-bin dist

install:
	install -Dm755 eazy $(DESTDIR)$(BINDIR)/eazy

uninstall:
	rm -f $(DESTDIR)$(BINDIR)/eazy

install-full:
	./eazy --install

compile-bin:
	./tools/compilar-eazy.sh eazy $(BIN_TARGET)

dist:
	command -v zip >/dev/null 2>&1 || { echo 'Erro: zip é necessário para gerar os pacotes de distribuição.' >&2; exit 1; }
	tar --exclude='__pycache__' --exclude='*.pyc' -czf $(DIST_STEM).tar.gz $(DIST_FILES)
	sha256sum $(DIST_STEM).tar.gz > $(DIST_STEM).tar.gz.sha256
	zip -X -r $(DIST_STEM).zip $(DIST_FILES) -x '*/__pycache__/*' '*.pyc' >/dev/null
	sha256sum $(DIST_STEM).zip > $(DIST_STEM).zip.sha256
