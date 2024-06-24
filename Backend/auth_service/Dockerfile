FROM alpine:3.20

ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

USER root
# Update and install dependencies
RUN apk update && apk add --no-cache \
	python3=3.12.3-r1 \
    py3-pip=24.0-r2 \
    postgresql16=16.3-r0 \
    postgresql16-client=16.3-r0 \
    bash=5.2.26-r0 && \
    mkdir /run/postgresql && \
    chown -R postgres:postgres /run/postgresql
WORKDIR /app/
RUN chown -R postgres:postgres /app/ && \
python3 -m venv venv && chown -R postgres:postgres venv

COPY --chown=postgres:postgres ./Backend/auth_service/requirements.txt .

# Copy the rest of the application code
COPY --chown=postgres:postgres ./Backend/auth_service/auth_service /app/auth_service

# Copy and set permissions for the entrypoint script
COPY --chown=postgres:postgres ./Backend/auth_service/tools.sh /app
COPY --chown=postgres:postgres ./Backend/auth_service/init_database.sh /app
RUN chmod +x /app/tools.sh /app/init_database.sh && chown -R postgres:postgres /app/auth_service/user_auth/
USER postgres

# Add HEALTHCHECK instruction with delay
HEALTHCHECK --interval=30s --timeout=2s --start-period=60s --retries=3 CMD curl -sSf http://localhost:8000/auth/api/token/ > /dev/null &&  echo "success" || echo "failure"
ENTRYPOINT [ "sh", "./tools.sh" ]
