#! /bin/sh

if [ ! -f '/etc/letsencrypt/live/fetap.net/fullchain.pem' ]; then
    certbot certonly --webroot --webroot-path /var/www/certbot/ -d fetap.net
else
    certbot renew
fi