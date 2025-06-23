.PHONY: install build-deb clean

export PACKAGE_NAME=video-source-py

default: build-deb

install:
	poetry install

check-settings:
	./check_settings.sh

build-deb: check-settings
	$(shell echo ${GPG_KEY} | base64 --decode | gpg --batch --import)
	$(eval KEYID := $(shell gpg --list-keys --with-colons | grep pub | cut -d: -f5))
	@echo "Signing with key id: $(KEYID)"

	poetry lock
	poetry build
	PASSPHRASE=${PASSPHRASE} dpkg-buildpackage -k$(KEYID)
	mkdir -p target
	mv ../${PACKAGE_NAME}_* target/

clean:
	rm -rf dist
	rm -rf target
	rm -rf *.egg-info
	rm -rf debian/.debhelper
	rm -f debian/files
	rm -f debian/*.substvars
	rm -f debian/*.log
	rm -f debian/debhelper-build-stamp
	rm -f debian/${PACKAGE_NAME}.postinst.debhelper
	rm -f debian/${PACKAGE_NAME}.postrm.debhelper
	rm -f debian/${PACKAGE_NAME}.prerm.debhelper
	rm -rf debian/${PACKAGE_NAME}
	rm -f *.tar.gz