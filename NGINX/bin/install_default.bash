#!/bin/bash

INSTALL="FALSE"
if [ "$1" == "install" ]; then
	NGINX_SERVER_BLOCK="tvvmia.rocks"
	NGINX_SERVER_HTML_LOCATION="/var/www/${NGINX_SERVER_BLOCK}/html"
	cp html/*.html "${NGINX_SERVER_HTML_LOCATION}"
	ls -la "${NGINX_SERVER_HTML_LOCATION}"
	cat "${NGINX_SERVER_HTML_LOCATION}/index.html"
else
	echo "Usage: sudo bash bin/install.bash install"
fi