FROM alpine:3.20

ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

# Update and install dependencies
RUN apk update && apk add --no-cache python3 py3-pip postgresql-client postgresql

# Set work directory
RUN mkdir /run/postgresql
RUN chown postgres:postgres /run/postgresql

WORKDIR /app/

COPY ./Backend/user_management/requirements.txt .
RUN python3.12 -m venv .env

# Copy the rest of the application code
COPY ./Backend/user_management/user_management /app/user_management 

# Copy and set permissions for the entrypoint script
COPY ./Backend/user_management/tools.sh /app
COPY ./Backend/user_management/init_database.sh /app
RUN chmod +x /app/tools.sh /app/init_database.sh

ENTRYPOINT [ "sh", "./tools.sh" ]