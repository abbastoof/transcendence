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
python3 /app/game_server/manage.py runserver 0.0.0.0:8002
# echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('$DB_USER', 'admin@example.com', '$DB_USER')" | python3 /app/auth_service/manage.py shell && echo "Superuser created successfully."
# CMD ["gunicorn", "auth_service.wsgi:application", "--bind", "0.0.0.0:8000"]
