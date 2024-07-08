#!/bin/bash

# Create necessary directories with appropriate permissions
cd /
mkdir -p /run/postgresql
chown postgres:postgres /run/postgresql/

# Initialize the database
initdb -D /var/lib/postgresql/data

# Switch to the postgres user and run the following commands
mkdir -p /var/lib/postgresql/data
initdb -D /var/lib/postgresql/data

# Append configurations to pg_hba.conf and postgresql.conf as the postgres user
echo "host all all 0.0.0.0/0 md5" >> /var/lib/postgresql/data/pg_hba.conf
echo "listen_addresses='*'" >> /var/lib/postgresql/data/postgresql.conf

# Remove the unix_socket_directories line from postgresql.conf as the postgres user
sed -i "/^unix_socket_directories = /d" /var/lib/postgresql/data/postgresql.conf

# Ensure the postgres user owns the data directory
chown -R postgres:postgres /var/lib/postgresql/data

# Start the PostgreSQL server as the postgres user, keeping it in the foreground
exec postgres -D /var/lib/postgresql/data &

# Wait for PostgreSQL to start (you may need to adjust the sleep time)
sleep 5

# # Create a new PostgreSQL user and set the password
psql -c "CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASS}';"
# psql -c "GRANT ALL PRIVILEGES ON SCHEMA public TO ${DB_USER};"
# psql -c "GRANT ALL PRIVILEGES ON DATABASE postgres TO ${DB_USER};"

# # Create the database named test_game_history_db.
# psql -c "CREATE DATABASE test_game_history_db;"
# psql -c "GRANT ALL PRIVILEGES ON DATABASE test_game_history_db TO ${DB_USER};"

# Grant all necessary privileges to the user
psql -c "ALTER USER ${DB_USER} CREATEDB;"
psql -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ${DB_USER};"
psql -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ${DB_USER};"
psql -c "GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO ${DB_USER};"

# Create the database named test_game_history_db.
psql -c "CREATE DATABASE test_game_history_db OWNER ${DB_USER};"
psql -c "GRANT ALL PRIVILEGES ON DATABASE test_game_history_db TO ${DB_USER};"


# Run Django migrations
cd /app
source venv/bin/activate
python manage.py migrate

# Stop the PostgreSQL server after setting the password
pg_ctl stop -D /var/lib/postgresql/data

sleep 5

# Start the PostgreSQL server as the postgres user, keeping it in the foreground
pg_ctl start -D /var/lib/postgresql/data
