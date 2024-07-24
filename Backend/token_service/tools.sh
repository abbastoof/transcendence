#! /bin/bash

# trunk-ignore(shellcheck/SC1091)
source venv/bin/activate
pip install --no-cache-dir -r /app/requirements.txt
pip install tzdata

while ! pgsql -h postgresql -U "${DB_USER}" -d "token_service"; do
    echo >&2 "Postgres is unavailable - sleeping"
    sleep 5
done

export DJANGO_SETTINGS_MODULE=token_service.settings

python3 /app/token_service/manage.py makemigrations
python3 /app/token_service/manage.py migrate
cd /app/token_service
daphne -b 0.0.0.0 -p 8000 token_service.asgi:application