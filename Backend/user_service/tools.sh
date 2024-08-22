#! /bin/bash

# trunk-ignore(shellcheck/SC1091)
source venv/bin/activate
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

# Wait for PostgreSQL to be available
while ! psql -h postgresql -U "${DB_USER}" -d "user_service" -c '\q'; do
	echo >&2 "Postgres is unavailable - sleeping"
	sleep 5
done

export DJANGO_SETTINGS_MODULE=user_service.settings
python3 /app/user_service/manage.py makemigrations user_app
python3 /app/user_service/manage.py migrate
cd /app/user_service
# exec uvicorn user_service.asgi:application --host 0.0.0.0 --port 8001
daphne -b 0.0.0.0 -p 8001 user_service.asgi:application
