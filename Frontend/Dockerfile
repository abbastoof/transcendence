FROM alpine:3.20 AS frontend

RUN apk update && apk add --no-cache nginx=1.26.1-r0 openrc=0.54-r1 openssl=3.3.1-r0 openssh=9.7_p1-r3 curl=8.7.1-r0 bash=5.2.26-r0

RUN addgroup -S www && adduser -D -S -G www www && \
mkdir -p /www && \
chown -R www:www /var/lib/nginx && \
chown -R www:www /var/lib/nginx/logs/ && \
chown -R www:www /www && \
mkdir -p /etc/nginx/ssl && \
chown -R www:www /etc/nginx/ssl && \
chown -R www:www /etc/nginx
COPY --chown=www:www ./Frontend/src /www/
WORKDIR /app
COPY --chown=www:www ./Frontend/tools.sh /app/tools.sh
RUN chmod +x /app/tools.sh

COPY --chown=www:www ./Frontend/nginx.conf /etc/nginx/nginx.conf
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD curl -sSf http://localhost:443 > /dev/null &&  echo "success" || echo "failure"
RUN chown -R www:www /run/nginx
USER www
CMD ["sh", "tools.sh"]
