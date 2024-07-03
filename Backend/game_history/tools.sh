#!/bin/bash

# Run the initialization script
sh /app/init_database.sh

# Activate the virtual environment and install dependencies
source venv/bin/activate
pip install -r requirements.txt
pip install tzdata

# Wait for PostgreSQL to be available
while ! pg_isready -q -U "${DB_USER}" -d "postgres"; do
	echo >&2 "Postgres is unavailable - sleeping"
	sleep 5
done

export DJANGO_SETTINGS_MODULE=game_history.settings

# Apply Django migrations

python3 /app/game_history/manage.py makemigrations game_data
python3 /app/game_history/manage.py makemigrations game_history
python3 /app/game_history/manage.py migrate

# Start the Django application
cd /app/game_history
daphne -b 0.0.0.0 -p 8002 game_history.asgi:application
