#! /bin/bash

# trunk-ignore(shellcheck/SC1091)
source venv/bin/activate
pip install --no-cache-dir -r /app/requirements.txt
pip install tzdata

# Wait for PostgreSQL to be available
while ! psql -h postgresql -U "${DB_USER}" -d "user_service" -c '\q'; do
	echo >&2 "Postgres is unavailable - sleeping"
	sleep 5
done

export DJANGO_SETTINGS_MODULE=user_service.settings
python3 /app/user_service/manage.py makemigrations user_app
python3 /app/user_service/manage.py migrate
# echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('${DB_USER}', 'admin@example.com', '${DB_USER}')" | python3 /app/user_service/manage.py shell && echo "Superuser created successfully."
# python3 /app/user_service/manage.py runserver 0.0.0.0:8001
cd /app/user_service
daphne -b 0.0.0.0 -p 8001 user_service.asgi:application
