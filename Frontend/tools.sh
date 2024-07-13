#! /bin/bash

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

nginx -g "daemon off;"