#! /bin/bash

openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/nginx/ssl/nginx-selfsigned.key \
	-out /etc/nginx/ssl/nginx-selfsigned.crt -subj \
	"/C=FI/ST=UUSIMAA/L=HELSINKI/O=HIVE/OU=HIVE/CN=localhost"
sleep 5

USER_SERVICE_URL="http://user-service:8001/user/register/"

# Wait until Django server is available
while ! curl -s "${USER_SERVICE_URL}" >/dev/null; do
	echo "Waiting for Django server at ${USER_SERVICE_URL}..."
	sleep 5
done

AUTH_SERVICE_URL="http://token-service:8000/"

# Wait until Django server is available
while ! curl -s "${AUTH_SERVICE_URL}" >/dev/null; do
	echo "Waiting for Django server at ${AUTH_SERVICE_URL}..."
	sleep 5
done

PROFILE_SERVICE_URL="http://profile-service:8004/"

# Wait until Django server is available
while ! curl -s "${PROFILE_SERVICE_URL}" >/dev/null; do
	echo "Waiting for Django server at ${PROFILE_SERVICE_URL}..."
	sleep 5
done


nginx -g "daemon off;"
