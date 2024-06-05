FROM alpine:3.20 AS frontend

RUN apk update && apk add nginx openrc openssl openssh

RUN adduser -D -g 'www' www
RUN mkdir /www
RUN chown -R www:www /var/lib/nginx
RUN chown -R www:www /www
COPY Frontend/index.html /www/index.html
COPY Frontend/tools.sh /tools.sh
RUN chmod +x /tools.sh
COPY Frontend/nginx.conf /etc/nginx/nginx.conf


CMD ["sh", "./tools.sh"]