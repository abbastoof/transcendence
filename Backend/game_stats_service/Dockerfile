FROM alpine:3.20

ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

# Update and install dependencies

RUN apk update && apk add --no-cache python3 py3-pip \
    postgresql16 postgresql16-client \
    bash supervisor curl openssl bash \
    build-base libffi-dev python3-dev

# Set work directory
RUN mkdir /run/postgresql && \
    chown postgres:postgres /run/postgresql && \
    mkdir /app && chown -R postgres:postgres /app

WORKDIR /app/

# Install Python virtual environment
RUN python3 -m venv venv && chown -R postgres:postgres venv

# Copy application code and adjust permissions
COPY --chown=postgres:postgres ./Backend/game_stats_service/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY --chown=postgres:postgres ./Backend/game_stats_service/requirements.txt .
COPY --chown=postgres:postgres ./Backend/game_stats_service/game_stats_service /app/game_stats_service
COPY --chown=postgres:postgres ./Backend/game_stats_service/tools.sh /app
COPY --chown=postgres:postgres ./Backend/game_stats_service/init_database.sh /app

# Install Python packages
RUN . venv/bin/activate && pip install -r requirements.txt

# Create log files and set permissions
RUN touch /var/log/django.log /var/log/django.err /var/log/init_database.log /var/log/init_database.err && \
    chown -R postgres:postgres /var/log/django.log /var/log/django.err /var/log/init_database.log /var/log/init_database.err

# Ensure supervisord and scripts are executable and owned by postgres
RUN chown -R postgres:postgres /app && \
    chown -R postgres:postgres /var/log && \
    chown -R postgres:postgres /app/venv && \
    chown -R postgres:postgres /app/game_stats_service

USER postgres

HEALTHCHECK --interval=30s --timeout=2s --start-period=5s --retries=3 CMD curl -sSf http://localhost:8003/game-stats/ > /dev/null && echo "success" || echo "failure"

ENTRYPOINT ["sh", "./tools.sh"]


