#!/bin/bash

if [ "" == "$1" ]; then
	echo "Usage: $0 [-o] [-c]"
	echo "	where:	-o == override everything"
	echo "		-c == reconfigure nginx only"
	exit
fi


OVERRIDE="FALSE"
if [ "$1" == "-o" ]; then
	OVERRIDE="TRUE"
fi
RECONFIGURE_NGINX="FALSE"
if [ "$1" == "-c" ]; then
	RECONFIGURE_NGINX="TRUE"
fi

function openssl_params() {
echo "US"
echo "Brooklyn"
echo "New York, NY"
echo "The Vinyl Villains, Ltd."
echo "Virrual Rock Band"
echo "tvvmia.rocks"
echo "nunya@bidnez.org"
}
echo "Using openssl to create self-signed key and certificate pair directly into nginx version: nginx/1.14.0 installation..."
NGINX_SSL_KEY_FILE="/etc/ssl/private/nginx-selfsigned.key"
NGINX_SSL_CERT_FILE="/etc/ssl/certs/nginx-selfsigned.crt"
if [ "TRUE" == "${OVERRIDE}" ]; then
	echo "Removing: ${NGINX_SSL_CERT_FILE} ${NGINX_SSL_KEY_FILE}"
	rm "${NGINX_SSL_CERT_FILE}" "${NGINX_SSL_KEY_FILE}"
fi
if [ ! -f "${NGINX_SSL_KEY_FILE}" -o ! -f "${NGINX_SSL_CERT_FILE}" ]; then
	openssl_params | openssl req -x509 -nodes -days 30 -newkey rsa:2048 -keyout "${NGINX_SSL_KEY_FILE}" -out "${NGINX_SSL_CERT_FILE}"
fi

if [ ! -f "${NGINX_SSL_KEY_FILE}" ]; then
	echo "Failed to create ${NGINX_SSL_KEY_FILE}"
	echo "Try running this with sudo."
	exit
fi
if [ ! -f "${NGINX_SSL_CERT_FILE}" ]; then
	echo "Failed to create ${NGINX_SSL_CERT_FILE}"
	echo "Try running this with sudo."
	exit
fi

SSL_CERT_DH_FILE="/etc/ssl/certs/dhparam.pem"
if [ "TRUE" == "${OVERRIDE}" -o ! -f "${SSL_CERT_DH_FILE}" ]; then
	echo "Creating Diffie-Hellman group, this step can take several seconds..."
	openssl dhparam -out "${SSL_CERT_DH_FILE}" 2048
fi

CERT_SNIPPET_FILE="/etc/nginx/snippets/self-signed.conf"
create_cert_snippet() {
echo "Creating a configuration snippet containing our SSL key and certificate file locations..."
cat <<+++CONF_SNIPPET_DATA+++ > "${CERT_SNIPPET_FILE}"
ssl_certificate /etc/ssl/certs/nginx-selfsigned.crt;
ssl_certificate_key /etc/ssl/private/nginx-selfsigned.key;
+++CONF_SNIPPET_DATA+++
}
if [ "TRUE" == "${OVERRIDE}" -o ! -f "${CERT_SNIPPET_FILE}" ]; then
	create_cert_snippet
fi
if [ ! -f "${CERT_SNIPPET_FILE}" ]; then
	echo "Failed to create CERT_SNIPPET_FILE: ${CERT_SNIPPET_FILE}"
	exit
fi

CONFIGURATION_SNIPPET_FILE="/etc/nginx/snippets/ssl-params.conf"
function create_config_snippet() {
echo "Creating a configuration snippet containing strong SSL settings that can be used with any certificates in the future..."
cat << +++CONF_DATA+++ > "${CONFIGURATION_SNIPPET_FILE}"
# from https://cipherli.st/
# and https://raymii.org/s/tutorials/Strong_SSL_Security_On_nginx.html
# SSL configuration settings
ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
ssl_prefer_server_ciphers on;
ssl_ciphers "EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH";
ssl_ecdh_curve secp384r1;
ssl_session_cache shared:SSL:10m;
ssl_session_tickets off;
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;
# Disable preloading HSTS for now.  You can use the commented out header line that includes
# the "preload" directive if you understand the implications.
#add_header Strict-Transport-Security "max-age=63072000; includeSubdomains; preload";
add_header Strict-Transport-Security "max-age=63072000; includeSubdomains";
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
#  Diffie-Hellman
ssl_dhparam /etc/ssl/certs/dhparam.pem;
+++CONF_DATA+++
}
if [ "TRUE" == "${OVERRIDE}" -o ! -f "${CONFIGURATION_SNIPPET_FILE}" ]; then
	create_config_snippet
fi
if [ ! -f "${CONFIGURATION_SNIPPET_FILE}" ]; then
	echo "Failed to create CONFIGURATION_SNIPPET_FILE: ${CONFIGURATION_SNIPPET_FILE}"
	exit
fi

NGINX_SERVER_BLOCK="tvvmia.rocks"
NGINX_SERVER_BLOCK_CONFIG_FILE="/etc/nginx/sites-available/${NGINX_SERVER_BLOCK}"
function backup_nginx_config() {
if [ -f "${NGINX_SERVER_BLOCK_CONFIG_FILE}.bak" ]; then
	echo "Adjusting our Nginx server blocks to handle SSL requests and use the two snippets above..."
	cp "${NGINX_SERVER_BLOCK_CONFIG_FILE}.bak" "${NGINX_SERVER_BLOCK_CONFIG_FILE}.bak1"
fi
echo "Backing up server-block ${NGINX_SERVER_BLOCK}..."
cp "${NGINX_SERVER_BLOCK_CONFIG_FILE}" "${NGINX_SERVER_BLOCK_CONFIG_FILE}.bak"
}

function install_nginx_config() {
backup_nginx_config
echo "Configuring nginx server-block: ${NGINX_SERVER_BLOCK}..."
cp nginx.conf "${NGINX_SERVER_BLOCK_CONFIG_FILE}"
}
if [ "TRUE" == "${OVERRIDE}" -o "TRUE" == "${RECONFIGURE_NGINX}" ]; then
	install_nginx_config
fi
if [ ! -f "${NGINX_SERVER_BLOCK_CONFIG_FILE}" ]; then
	echo "Failed to create NGINX_SERVER_BLOCK_CONFIG_FILE: ${NGINX_SERVER_BLOCK_CONFIG_FILE}"
	exit
fi

function restart_nginx() {
echo "Restarting NGINX..."
systemctl restart nginx
}

echo "Applying new configuration to NGINX..."
ufw status
ufw allow 'Nginx Full'
ufw delete allow 'Nginx HTTP'
ufw status
NGINX_TEST="/tmp/${NGINX_SERVER_BLOCK}"
nginx -t &> "${NGINX_TEST}"
cat ${NGINX_TEST}
NGINX_OK="`cat ${NGINX_TEST} | grep 'syntax is ok'`"
echo "<NGINX_OK>=<${NGINX_OK}>"
if [ "" != "${NGINX_OK}" ]; then
	echo "congrats, looks like it worked."
	restart_nginx
else
	echo "oh no, looks like test failed."
	cat ${NGINX_TEST}
fi
