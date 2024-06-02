#! /bin/bash

# Create necessary directories with appropriate permissions
mkdir -p /run/postgresql
chown postgres:postgres /run/postgresql/

# Switch to the postgres user and run the following commands
su - postgres -c "mkdir -p /var/lib/postgresql/data"
su - postgres -c "initdb -D /var/lib/postgresql/data"

# Append configurations to pg_hba.conf and postgresql.conf as the postgres user
su - postgres -c "echo \"host all all 0.0.0.0/0 md5\" >> /var/lib/postgresql/data/pg_hba.conf"
su - postgres -c "echo \"listen_addresses='*'\" >> /var/lib/postgresql/data/postgresql.conf"

# Remove the unix_socket_directories line from postgresql.conf as the postgres user
su - postgres -c "sed -i \"/^unix_socket_directories = /d\" /var/lib/postgresql/data/postgresql.conf"

# Ensure the postgres user owns the data directory
chown -R postgres:postgres /var/lib/postgresql/data

# Start the PostgreSQL server as the postgres user, keeping it in the foreground
exec su - postgres -c "postgres -D /var/lib/postgresql/data" &

# Wait for PostgreSQL to start (you may need to adjust the sleep time)
sleep 5

# Create a new PostgreSQL user and set the password
su - postgres -c "psql -c \"CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';\""
su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON SCHEMA public TO $DB_USER;\""
su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE postgres TO $DB_USER;\""

# Stop the PostgreSQL server after setting the password
su - postgres -c "pg_ctl stop -D /var/lib/postgresql/data"

sleep 5
# Start the PostgreSQL server as the postgres user, keeping it in the foreground
exec su - postgres -c "postgres -D /var/lib/postgresql/data"
