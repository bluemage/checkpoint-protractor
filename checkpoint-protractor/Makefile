.PHONY: all deb clean

all:
	@echo "Use 'make deb' to build the Debian package."

deb:
	dpkg-buildpackage -us -uc -b

clean:
	rm -rf debian/checkpoint-protractor debian/tmp debian/files debian/*.substvars debian/debhelper-build-stamp debian/.debhelper
	rm -f ../checkpoint-protractor_*.deb ../checkpoint-protractor_*.changes ../checkpoint-protractor_*.buildinfo ../checkpoint-protractor_*.dsc ../checkpoint-protractor_*.tar.*
