#! /bin/bash

sh /app/init_database.sh
# trunk-ignore(shellcheck/SC1091)
source venv/bin/activate
pip install -r requirements.txt
pip install tzdata

while ! psql -U "${DB_USER}" -d "postgres" -c '\q'; do
	echo >&2 "Postgres is unavailable - sleeping"
	sleep 5
done

export DJANGO_SETTINGS_MODULE=profile_service.settings

python3 /app/profile_service/manage.py makemigrations
python3 /app/profile_service/manage.py migrate
cd /app/profile_service
daphne -b 0.0.0.0 -p 8004 profile_service.asgi:application
