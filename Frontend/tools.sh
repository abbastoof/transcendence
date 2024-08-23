#!/bin/bash

# Wait until the Django server is available
while ! curl -s "${USER_SERVICE}" >/dev/null; do
    echo "Waiting for user-service server at ${USER_SERVICE}..."
    sleep 5
done

# Wait until the Auth server is available
while ! curl -s "${TOKEN_SERVICE}" >/dev/null; do
    echo "Waiting for token-service at ${TOKEN_SERVICE}..."
    sleep 5
done

# Wait until the Auth server is available
while ! curl -s "${GAME_HISTORY}" >/dev/null; do
    echo "Waiting for game-history at ${GAME_HISTORY}..."
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
