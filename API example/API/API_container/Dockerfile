FROM alpine:3.20

ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

# Update and install dependencies
RUN apk update && apk add --no-cache python3 py3-pip postgresql-client postgresql

# Set work directory

RUN mkdir /run/postgresql
RUN chown postgres:postgres /run/postgresql

# Set work directory
WORKDIR /app/

COPY ./API/requirements.txt .
RUN python3.12 -m venv .env
RUN source .env/bin/activate

# Copy the rest of the application code
COPY ./admin /app/admin

# Copy and set permissions for the entrypoint script
COPY ./API/API_container/tools.sh /app
COPY ./API/API_container/init_database.sh /app
RUN chmod +x /app/tools.sh /app/init_database.sh

ENTRYPOINT [ "sh", "./tools.sh" ]