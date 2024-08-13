FROM python:3.11-alpine3.20

ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

# Update and install dependencies
# trunk-ignore(hadolint/DL3018)
RUN apk add --no-cache supervisor \
    curl openssl bash postgresql16-client \
    build-base libffi-dev python3-dev

RUN mkdir /app && chown -R postgres:postgres /app

WORKDIR /app/

# Install Python virtual environment
RUN python3 -m venv venv && chown -R postgres:postgres venv
RUN touch /var/log/django_debug.log && chown -R postgres:postgres /var/log/django_debug.log
RUN touch /var/log/django_error.log && chown -R postgres:postgres /var/log/django_error.log

# Copy application code and adjust permissions
COPY --chown=postgres:postgres ./Backend/game_history/requirements.txt .
COPY --chown=postgres:postgres ./Backend/game_history/game_history /app/game_history
COPY --chown=postgres:postgres ./Backend/game_history/tools.sh /app

# Ensure supervisord and scripts are executable and owned by postgres
RUN chown -R postgres:postgres /app && \
    chown -R postgres:postgres /var/log && \
    chown -R postgres:postgres /app/venv && \
    chown -R postgres:postgres /app/game_history

USER postgres

HEALTHCHECK --interval=30s --timeout=2s --start-period=5s --retries=3 CMD curl -sSf http://localhost:8002/game-history/ > /dev/null && echo "success" || echo "failure"

ENTRYPOINT ["sh", "/app/tools.sh"]
