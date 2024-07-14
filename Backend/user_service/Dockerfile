FROM alpine:3.20

ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

# Update and install dependencies
# trunk-ignore(hadolint/DL3018)
RUN apk update && apk add --no-cache python3 py3-pip \
postgresql16 postgresql16-client \
bash supervisor curl openssl bash \
build-base libffi-dev python3-dev nano
# Set work directory
RUN mkdir /run/postgresql && \
    chown postgres:postgres /run/postgresql && \
    mkdir /app && chown -R postgres:postgres /app

WORKDIR /app/

# Install Python virtual environment
RUN python3 -m venv venv && chown -R postgres:postgres venv

# Copy application code and adjust permissions
COPY --chown=postgres:postgres ./Backend/user_service/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY --chown=postgres:postgres ./Backend/user_service/requirements.txt /app/
COPY --chown=postgres:postgres ./Backend/user_service/user_service /app/user_service
COPY --chown=postgres:postgres ./Backend/user_service/tools.sh /app
COPY --chown=postgres:postgres ./Backend/user_service/init_database.sh /app
COPY --chown=postgres:postgres ./Backend/user_service/run_consumer.sh /app
RUN chmod +x /app/tools.sh /app/init_database.sh /app/run_consumer.sh

# Ensure supervisord and scripts are executable and owned by postgres
RUN chown -R postgres:postgres /etc/supervisor && \
    chown -R postgres:postgres /usr/bin/supervisord && \
    chown -R postgres:postgres /etc/supervisor/conf.d/supervisord.conf && \
    chown -R postgres:postgres /app && \
    chown -R postgres:postgres /var/log && \
    chown -R postgres:postgres /app/venv && \
    chown -R postgres:postgres /app/user_service && \
    chmod +x /usr/bin/supervisord

USER root

HEALTHCHECK --interval=30s --timeout=2s --start-period=5s --retries=3 CMD curl -sSf http://localhost:8001/user/register/ > /dev/null &&  echo "success" || echo "failure"

ENTRYPOINT ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
