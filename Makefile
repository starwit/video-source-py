.PHONY: install build-deb clean

install:
	poetry install

check-settings:
	./check_settings.sh

build-deb: check-settings
	poetry lock
	poetry build
	dpkg-buildpackage -us -uc
	mkdir -p target
	mv ../video-source-py_* target/

clean:
	rm -rf dist
	rm -rf target
	rm -rf *.egg-info
	rm -rf debian/.debhelper
	rm -f debian/files
	rm -f debian/*.substvars
	rm -f debian/*.log
	rm -f debian/debhelper-build-stamp
	rm -f debian/video-source-py.postinst.debhelper
	rm -f debian/video-source-py.prerm.debhelper
	rm -rf debian/video-source-py
	rm -f *.tar.gz