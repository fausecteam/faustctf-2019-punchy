.PHONY: all

all:
	rm -rf dist_root
	rm -rf .venv

	./build-venv.sh

	sed -i '769i\ \ \ \ \ \ \ \ return' .venv/lib/python3.*/site-packages/werkzeug/contrib/cache.py

	mkdir -p dist_root/srv/punchy/

	cp *.py dist_root/srv/punchy
	cp -r .venv dist_root/srv/punchy/

	mkdir -p dist_root/srv/punchy/extensions/join
	mkdir -p dist_root/srv/punchy/extensions/staply
	mkdir -p dist_root/srv/punchy/extensions/decode

	make -C extensions

	strip extensions/join/*.so
	strip extensions/staply/*.so
	strip extensions/decode/*.so

	cp extensions/join/*.so   dist_root/srv/punchy/extensions/join/
	cp extensions/staply/*.so dist_root/srv/punchy/extensions/staply/
	cp extensions/decode/*.so dist_root/srv/punchy/extensions/decode/

	mkdir -p dist_root/etc/nginx/sites-enabled/
	cp meta/punchy.conf dist_root/etc/nginx/sites-enabled/

	mkdir -p dist_root/etc/uwsgi/apps-enabled/
	cp meta/punchy.ini dist_root/etc/uwsgi/apps-enabled/

	extensions/crypto/crypto staply.html > staply.enc
	cp *.enc dist_root/srv/punchy/

	cp -r static/ dist_root/srv/punchy/static
	cp -r templates/ dist_root/srv/punchy/templates
