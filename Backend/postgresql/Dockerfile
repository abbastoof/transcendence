FROM alpine:3.20

RUN apk add --no-cache postgresql16 && mkdir /run/postgresql && \
    chown postgres:postgres /run/postgresql
WORKDIR /app
COPY ./Backend/postgresql/init_database.sh /app
RUN chmod +x /app/init_database.sh
USER postgres

CMD ["sh", "./init_database.sh"]
