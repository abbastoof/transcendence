FROM alpine:3.20

ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

# Update and install dependencies
RUN apk update && apk add --no-cache python3 py3-pip postgresql-client postgresql bash

USER root
# Set work directory
RUN mkdir /run/postgresql
RUN chown postgres:postgres /run/postgresql

WORKDIR /app/
RUN chown -R postgres:postgres /app/

RUN python3.12 -m venv venv && chown -R postgres:postgres venv

COPY ./Backend/auth_service/requirements.txt .

# Copy the rest of the application code
COPY ./Backend/auth_service/auth_service /app/auth_service

# Copy and set permissions for the entrypoint script
COPY ./Backend/auth_service/tools.sh /app
COPY ./Backend/auth_service/init_database.sh /app
RUN chmod +x /app/tools.sh /app/init_database.sh && chown -R postgres:postgres /app/auth_service/user_auth/
USER postgres

# Add HEALTHCHECK instruction
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 CMD wget -q --spider http://localhost:8000/auth/api/token/ || exit 1
ENTRYPOINT [ "sh", "./tools.sh" ]
