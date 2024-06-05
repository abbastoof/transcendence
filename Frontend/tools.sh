#! /bin/bash

mkdir -p /etc/nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048\
            -keyout /etc/nginx/ssl/nginx-selfsigned.key \
            -out /etc/nginx/ssl/nginx-selfsigned.crt -subj \
            "/C=FI/ST=UUSIMAA/L=HELSINKI/O=HIVE/OU=HIVE/CN=localhost"
sleep 5
nginx -g "daemon off;"