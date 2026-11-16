PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin
VERSION = 5.1.3
BIN_DIR = bin
BIN_TARGET = $(BIN_DIR)/eazy-linux-x86_64

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
	tar -czf eazy-$(VERSION).tar.gz eazy eazy-index.py eazy-yt-stream eazy-tor eazy-ai.py eazy-notes-editor eazy.desktop eazy.1 README.md README_BETA_5.1.3.md RELEASE_5.1.3.md CHANGELOG.md EAZY_EXPLICADO.md GUIA_RAPIDO.md VERSION Makefile run-beta.sh docs/eazy-help-5.1.3.txt docs/eazy-help-5.1.3.html
