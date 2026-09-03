PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin
VERSION = 3.2

.PHONY: install uninstall install-full dist

install:
	install -Dm755 eazy $(DESTDIR)$(BINDIR)/eazy

uninstall:
	rm -f $(DESTDIR)$(BINDIR)/eazy

install-full:
	./eazy --install

dist:
	tar -czf eazy-$(VERSION).tar.gz eazy README.md install.sh uninstall.sh Makefile
