#! /bin/bash

export PGPASSWORD='root'
source .env/bin/activate
pip install -r requirements.txt
pip install tzdata

while ! psql -h "database" -U "$DB_USER" -d "postgres" -c '\q'; do
	>&2 echo "Postgres is unavailable - sleeping"
	sleep 5
done

python3 /app/admin/manage.py makemigrations
python3 /app/admin/manage.py migrate
python3 /app/admin/manage.py runserver 0.0.0.0:8000