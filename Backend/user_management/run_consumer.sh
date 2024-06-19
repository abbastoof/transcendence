#!/bin/bash

# URL of the Django application
DJANGO_URL="http://localhost:8000/user/register/"

# Wait until Django server is available
while ! curl -s $DJANGO_URL > /dev/null; do
    echo "Waiting for Django server at $DJANGO_URL..."
    sleep 5
done


source .env/bin/activate
python3 /app/user_management/consumer.py
echo "Django server is up at $DJANGO_URL"
exec "$@"