FROM alpine:3.20

# Update and install dependencies

RUN apk update && \
apk add --no-cache postgresql

# Set work directory

RUN mkdir /run/postgresql
RUN chown postgres:postgres /run/postgresql


# Copy and set permissions for the entrypoint script
COPY API/Database_container/tools.sh .
RUN chmod +x tools.sh

EXPOSE 5432

ENTRYPOINT [ "sh", "./tools.sh" ]