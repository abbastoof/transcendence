FROM alpine:3.20

ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

# Update and install dependencies
RUN apk update && apk add --no-cache \
python3=3.12.3-r1 py3-pip=24.0-r2 \
postgresql16=16.3-r0 postgresql16-client=16.3-r0 \
bash=5.2.26-r0 supervisor=4.2.5-r5 curl=8.8.0-r0
# Set work directory
RUN mkdir /run/postgresql && \
    chown postgres:postgres /run/postgresql && \
    mkdir /app && chown -R postgres:postgres /app

WORKDIR /app/

# Install Python virtual environment
RUN python3 -m venv venv && chown -R postgres:postgres venv

# Copy application code and adjust permissions
COPY --chown=postgres:postgres ./Backend/user_management/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY --chown=postgres:postgres ./Backend/user_management/requirements.txt .
COPY --chown=postgres:postgres ./Backend/user_management/user_management /app/user_management
COPY --chown=postgres:postgres ./Backend/user_management/tools.sh /app
COPY --chown=postgres:postgres ./Backend/user_management/init_database.sh /app
COPY --chown=postgres:postgres ./Backend/user_management/run_consumer.sh /app
RUN chmod +x /app/tools.sh /app/init_database.sh /app/run_consumer.sh

# Ensure supervisord and scripts are executable and owned by postgres
RUN chown -R postgres:postgres /etc/supervisor && \
    chown -R postgres:postgres /usr/bin/supervisord && \
    chown -R postgres:postgres /etc/supervisor/conf.d/supervisord.conf && \
    chown -R postgres:postgres /app && \
    chown -R postgres:postgres /var/log && \
    chown -R postgres:postgres /app/venv && \
    chown -R postgres:postgres /app/user_management && \
    chmod +x /usr/bin/supervisord

USER postgres

HEALTHCHECK --interval=30s --timeout=2s --start-period=5s --retries=3 CMD curl -sSf http://localhost:8000/user/register/ > /dev/null &&  echo "success" || echo "failure"

ENTRYPOINT ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
