#! /bin/bash

sh /app/init_database.sh

source venv/bin/activate
pip install -r requirements.txt
pip install tzdata

while ! psql -U "${DB_USER}" -d "postgres" -c '\q'; do
	echo >&2 "Postgres is unavailable - sleeping"
	sleep 5
done
export DJANGO_SETTINGS_MODULE=user_management.settings
python3 /app/user_management/manage.py makemigrations users
python3 /app/user_management/manage.py migrate
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('${DB_USER}', 'admin@example.com', '${DB_USER}')" | python3 /app/user_management/manage.py shell && echo "Superuser created successfully."
# python3 /app/user_management/manage.py runserver 0.0.0.0:8001
cd /app/user_management
daphne -b 0.0.0.0 -p 8001 user_management.asgi:application
