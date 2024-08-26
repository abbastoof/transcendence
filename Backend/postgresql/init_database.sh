#! /bin/bash

# Stop any running PostgreSQL processes
pg_ctl stop -D /var/lib/postgresql/data || true

# Remove any existing data directory
rm -rf /var/lib/postgresql/data

# Create necessary directories with appropriate permissions
mkdir -p /var/lib/postgresql/data
chown postgres:postgres /var/lib/postgresql/data
mkdir -p /run/postgresql
chown postgres:postgres /run/postgresql/

# Initialize the PostgreSQL data directory
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

# Create a new PostgreSQL user and set the password
psql -c "CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASS}';"
psql -c "ALTER USER ${DB_USER} CREATEDB;"

psql -c "CREATE DATABASE game_history;"
psql -c "CREATE DATABASE game_server;"
psql -c "CREATE DATABASE user_service;"
psql -c "CREATE DATABASE token_service;"

# Grant the new user all privileges on the database
psql -d user_service -c "GRANT ALL PRIVILEGES ON SCHEMA public TO ${DB_USER};"
psql -d user_service -c "GRANT ALL PRIVILEGES ON DATABASE user_service TO ${DB_USER};"
psql -d token_service -c "GRANT ALL PRIVILEGES ON SCHEMA public TO ${DB_USER};"
psql -d token_service -c "GRANT ALL PRIVILEGES ON DATABASE token_service TO ${DB_USER};"
psql -d game_history -c "GRANT ALL PRIVILEGES ON SCHEMA public TO ${DB_USER};"
psql -d game_history -c "GRANT ALL PRIVILEGES ON DATABASE game_history TO ${DB_USER};"
psql -d game_server -c "GRANT ALL PRIVILEGES ON SCHEMA public TO ${DB_USER};"
psql -d game_server -c "GRANT ALL PRIVILEGES ON DATABASE game_server TO ${DB_USER};"

psql -c "GRANT ALL PRIVILEGES ON DATABASE postgres TO ${DB_USER};"

# Stop the PostgreSQL server after setting the password
pg_ctl stop -D /var/lib/postgresql/data

sleep 5
# Start the PostgreSQL server as the postgres user, keeping it in the foreground
exec postgres -D /var/lib/postgresql/data
