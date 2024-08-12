#! /bin/bash

# trunk-ignore(shellcheck/SC1091)
source venv/bin/activate
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

while ! psql -h postgresql -U "${DB_USER}" -d "token_service" -c '\q'; do
	echo >&2 "Postgres is unavailable - sleeping"
	sleep 5
done

export DJANGO_SETTINGS_MODULE=token_service.settings

python3 /app/token_service/manage.py makemigrations
python3 /app/token_service/manage.py migrate
cd /app/token_service
# exec uvicorn token_service.asgi:application --host 0.0.0.0 --port 8000
daphne -b 0.0.0.0 -p 8000 token_service.asgi:application