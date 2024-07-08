#! /bin/bash

sh /app/init_database.sh

# trunk-ignore(shellcheck/SC1091)
source venv/bin/activate
pip install -r requirements.txt
pip install tzdata

# Wait for PostgreSQL to be available
while ! pg_isready -q -U "${DB_USER}" -d "postgres"; do
	echo >&2 "Postgres is unavailable - sleeping"
	sleep 5
done

python3 /app/game_server/manage.py makemigrations
python3 /app/game_server/manage.py migrate
cd /app/game_server
daphne -b 0.0.0.0 -p 8002 game_server_project.asgi:application
