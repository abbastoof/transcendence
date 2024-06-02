FROM alpine:3.20

ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

# Update and install dependencies
RUN apk update && apk add --no-cache python3 py3-pip postgresql-client

# Set work directory
WORKDIR /app/

COPY ./API/requirements.txt .
RUN python3.12 -m venv .env
RUN source .env/bin/activate

# Copy the rest of the application code
COPY ./admin /app/admin

# Copy and set permissions for the entrypoint script
COPY ./API/API_container/tools.sh /app
RUN chmod +x tools.sh

ENTRYPOINT [ "sh", "./tools.sh" ]