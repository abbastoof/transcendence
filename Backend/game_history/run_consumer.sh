# Backend/game_history/run_consumer.sh
#!/bin/bash

# URL of the Django application
DJANGO_URL="http://localhost:8002/some-endpoint/"  # Adjust the endpoint as necessary

# Wait until Django server is available
while ! curl -s "${DJANGO_URL}" >/dev/null; do
    echo "Waiting for Django server at ${DJANGO_URL}..."
    sleep 5
done

# Activate the virtual environment and start the consumer
source venv/bin/activate
python /app/game_history/consumer.py
echo "Django server is up at ${DJANGO_URL}"
exec "$@"
