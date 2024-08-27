FROM alpine:3.20

RUN apk add --no-cache postgresql16 && mkdir /run/postgresql && \
    chown postgres:postgres /run/postgresql
WORKDIR /app
COPY ./Backend/postgresql/init_database.sh /app
RUN chmod +x /app/init_database.sh
USER postgres
HEALTHCHECK --interval=30s --timeout=2s --start-period=5s --retries=3 CMD pg_isready -U postgres > /dev/null &&  echo "success" || echo "failure"

CMD ["sh", "./init_database.sh"]
