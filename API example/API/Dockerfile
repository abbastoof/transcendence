FROM alpine:3.20

ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

# Update and install dependencies
RUN apk update && apk add --no-cache python3 py3-pip postgresql-client postgresql

# Set work directory
RUN mkdir /run/postgresql
RUN chown postgres:postgres /run/postgresql

WORKDIR /app/
COPY ./API/requirements.txt .
RUN python3.12 -m venv .env

# Copy the rest of the application code
# COPY ./API/auth /app/auth // Copy the app

# Copy and set permissions for the entrypoint script
COPY ./API/tools.sh /app
COPY ./API/init_database.sh /app
RUN chmod +x /app/tools.sh /app/init_database.sh

ENTRYPOINT [ "sh", "./tools.sh" ]