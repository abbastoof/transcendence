FROM alpine:3.20

ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

USER root
# Update and install dependencies
# trunk-ignore(hadolint/DL3018)
RUN apk update && apk add --no-cache python3 py3-pip \
    postgresql16 postgresql16-client \
    bash supervisor curl openssl bash \
    build-base libffi-dev python3-dev nano && \
    mkdir /run/postgresql && \
    chown -R postgres:postgres /run/postgresql
WORKDIR /app/
RUN chown -R postgres:postgres /app/ && \
python3 -m venv venv && chown -R postgres:postgres venv

COPY --chown=postgres:postgres ./Game_server/requirements.txt .

# Copy the rest of the application code
COPY --chown=postgres:postgres ./Game_server/game_server_project/ /app/game_server

# Copy and set permissions for the entrypoint script
COPY --chown=postgres:postgres ./Game_server/tools.sh /app
COPY --chown=postgres:postgres ./Game_server/init_database.sh /app
RUN chmod +x /app/tools.sh /app/init_database.sh && chown -R postgres:postgres /app/game_server
USER postgres

# Add HEALTHCHECK instruction with delay
# HEALTHCHECK --interval=30s --timeout=2s --start-period=60s --retries=3 CMD curl -sSf http://localhost:8000/auth/api/token/ > /dev/null &&  echo "success" || echo "failure"
ENTRYPOINT [ "sh", "./tools.sh" ]
