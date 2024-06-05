#! /bin/bash

export PGPASSWORD='root'
sh /app/init_database.sh
source .env/bin/activate
pip install -r requirements.txt
pip install tzdata

while ! psql -U "$DB_USER" -d "postgres" -c '\q'; do
	>&2 echo "Postgres is unavailable - sleeping"
	sleep 5
done

python3 /app/auth/manage.py makemigrations users
python3 /app/auth/manage.py migrate
python3 /app/auth/manage.py runserver 0.0.0.0:8000