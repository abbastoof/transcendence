FROM alpine:3.20 AS frontend

# trunk-ignore(hadolint/DL3018)
RUN apk update && apk add --no-cache nginx openrc openssl openssh curl bash

RUN addgroup -S www && adduser -D -S -G www www && \
mkdir -p /www && \
chown -R www:www /var/lib/nginx && \
chown -R www:www /var/lib/nginx/logs/ && \
chown -R www:www /www && \
mkdir -p /etc/nginx/ssl && \
chown -R www:www /etc/nginx/ssl && \
chown -R www:www /etc/nginx
COPY --chown=www:www ./Frontend/src /www/
COPY --chown=www:www ./Frontend/default.jpg /www/avatars/
WORKDIR /app
COPY --chown=www:www ./Frontend/tools.sh /app/tools.sh
RUN chmod +x /app/tools.sh

COPY --chown=www:www ./Frontend/nginx.conf /etc/nginx/nginx.conf
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/nginx/ssl/nginx-selfsigned.key \
-out /etc/nginx/ssl/nginx-selfsigned.crt -subj \
"/C=FI/ST=UUSIMAA/L=HELSINKI/O=HIVE/OU=HIVE/CN=localhost"

RUN chmod 600 /etc/nginx/ssl/nginx-selfsigned.key /etc/nginx/ssl/nginx-selfsigned.crt && \
    chown -R www:www /var/lib/nginx/logs/ /run/nginx /etc/nginx/ssl

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD curl -sSf http://localhost:443 > /dev/null &&  echo "success" || echo "failure"
RUN chown -R www:www /run/nginx
USER www
CMD ["sh", "tools.sh"]
