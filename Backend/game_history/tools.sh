#!/bin/bash

# Activate the virtual environment
source venv/bin/activate
pip install --no-cache-dir -r requirements.txt
pip install tzdata

# Wait for PostgreSQL to be available
while ! psql -h postgresql -U "${DB_USER}" -d "game_history" -c '\q'; do
	echo >&2 "Postgres is unavailable - sleeping"
	sleep 5
done

# Export Django settings and PYTHONPATH
export DJANGO_SETTINGS_MODULE=game_history.settings
export PYTHONPATH=/app

# Debugging steps
echo "PYTHONPATH: $PYTHONPATH"
echo "Contents of /app:"
ls /app
echo "Contents of /app/game_history:"
ls /app/game_history

# Apply Django migrations
python3 /app/game_history/manage.py makemigrations
python3 /app/game_history/manage.py migrate

# Run pytest with explicit PYTHONPATH
# PYTHONPATH=/app pytest -vv

# Start the Django application
cd /app/game_history
daphne -b 0.0.0.0 -p 8002 game_history.asgi:application
