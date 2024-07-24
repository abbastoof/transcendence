FROM python:3.11-alpine3.20

ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

# Update and install dependencies
# trunk-ignore(hadolint/DL3018)
RUN apk add --no-cache postgresql16-client \
    bash supervisor curl openssl \
    build-base libffi-dev python3-dev
# Set work directory
RUN mkdir /run/postgresql && \
    chown postgres:postgres /run/postgresql && \
    mkdir /app && chown -R postgres:postgres /app

WORKDIR /app/

# Install Python virtual environment
RUN python3 -m venv venv && chown -R postgres:postgres venv

# Copy application code and adjust permissions
COPY --chown=postgres:postgres ./Backend/token_service/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY --chown=postgres:postgres ./Backend/token_service/requirements.txt /app/
COPY --chown=postgres:postgres ./Backend/token_service/token_service /app/token_service
COPY --chown=postgres:postgres ./Backend/token_service/tools.sh /app
COPY --chown=postgres:postgres ./Backend/token_service/run_consumer.sh /app
COPY --chown=postgres:postgres ./Backend/token_service/run_consumer2.sh /app
COPY --chown=postgres:postgres ./Backend/token_service/run_consumer3.sh /app

# Ensure supervisord and scripts are executable and owned by postgres
RUN chown -R postgres:postgres /etc/supervisor && \
    chown -R postgres:postgres /usr/bin/supervisord && \
    chown -R postgres:postgres /etc/supervisor/conf.d/supervisord.conf && \
    chown -R postgres:postgres /app && \
    chown -R postgres:postgres /var/log && \
    chown -R postgres:postgres /app/venv && \
    chown -R postgres:postgres /app/token_service && \
    chmod +x /usr/bin/supervisord

USER postgres

HEALTHCHECK --interval=30s --timeout=2s --start-period=5s --retries=3 CMD curl --fail --silent --write-out http://127.0.0.1:8000/ > /dev/null &&  echo "success" || echo "failure"

ENTRYPOINT ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
