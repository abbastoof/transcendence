#!/bin/bash

# Wait until the Django server is available
while ! curl -s "${USER_SERVICE_URL}" >/dev/null; do
    echo "Waiting for Django server at ${USER_SERVICE_URL}..."
    sleep 5
done

# Wait until the Auth server is available
while ! curl -s "${AUTH_SERVICE_URL}" >/dev/null; do
    echo "Waiting for Auth server at ${AUTH_SERVICE_URL}..."
    sleep 5
done

# Wait until the Auth server is available
while ! curl -s "${GAME_HISTORY_URL}" >/dev/null; do
    echo "Waiting for Auth server at ${GAME_HISTORY_URL}..."
    sleep 5
done

if [ "$NODE_ENV" = "development" ]; then
    echo "Starting Vite development server"
    # Run Vite in the background
    npm run dev &
    # Start Nginx in the foreground
    echo "Starting Nginx"
    nginx -g "daemon off;"
else
    echo "Starting Nginx"
    nginx -g "daemon off;"
fi
