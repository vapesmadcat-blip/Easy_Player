PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin
VERSION = 3.2.2
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
	tar -czf eazy-$(VERSION).tar.gz eazy README.md INSTALL.md install.sh Makefile
