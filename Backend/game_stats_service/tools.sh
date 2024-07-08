#!/bin/bash

# Initialize the database
sh /app/init_database.sh

# Activate the virtual environment
source venv/bin/activate
pip install -r requirements.txt
pip install tzdata

# Wait for PostgreSQL to be available
while ! pg_isready -q -U "${DB_USER}" -d "postgres"; do
    echo >&2 "Postgres is unavailable - sleeping"
    sleep 5
done

# Export Django settings and PYTHONPATH
export DJANGO_SETTINGS_MODULE=game_stats_service.settings
export PYTHONPATH=/app

# Debugging steps
echo "PYTHONPATH: $PYTHONPATH"
echo "Contents of /app:"
ls /app
echo "Contents of /app/game_stats_service:"
ls /app/game_stats_service

# Apply Django migrations
python3 /app/game_stats_service/manage.py makemigrations
python3 /app/game_stats_service/manage.py migrate

# Run pytest with explicit PYTHONPATH
PYTHONPATH=/app pytest -vv

# Start the Django application
cd /app/game_stats_service
daphne -b 0.0.0.0 -p 8003 game_stats_service.asgi:application
