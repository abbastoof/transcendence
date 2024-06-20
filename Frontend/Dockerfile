FROM alpine:3.20 AS frontend

RUN apk update && apk add --no-cache nginx openrc openssl openssh

RUN addgroup -S www && adduser -D -S -G www www && \
mkdir -p /www && \
chown -R www:www /var/lib/nginx && \
chown -R www:www /www && \
mkdir -p /etc/nginx/ssl && \
chown -R www:www /etc/nginx/ssl
COPY --chown=www:www Frontend/index.html /www/index.html
COPY --chown=www:www Frontend/tools.sh /tools.sh
RUN chmod +x /tools.sh
COPY --chown=www:www Frontend/nginx.conf /etc/nginx/nginx.conf
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD curl --fail http://localhost:443 || exit 1
USER www
CMD ["sh", "./tools.sh"]