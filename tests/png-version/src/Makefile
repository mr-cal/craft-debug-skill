all: png-version

png-version: main.c
	gcc -o png-version main.c -lpng

install:
	install -Dm755 png-version $(DESTDIR)/usr/bin/png-version

clean:
	rm -f png-version
