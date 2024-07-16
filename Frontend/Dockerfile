FROM alpine:3.20 AS frontend

# trunk-ignore(hadolint/DL3018)
RUN apk update && apk add --no-cache nginx openrc openssl openssh curl bash nodejs npm

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

# # Copy package.json and package-lock.json
COPY --chown=www:www ./Frontend/package.json /app/package.json
COPY --chown=www:www ./Frontend/package-lock.json /app/package-lock.json
COPY --chown=www:www ./Frontend/vite.config.js /app/vite.config.js

# Copy your frontend application files
WORKDIR /app
#COPY --chown=www:www ./Frontend/index.html /app/index.html
COPY --chown=www:www ./Frontend/src /app/src
RUN chown -R www:www /app

# Install npm dependencies and build the project
RUN npm cache clean --force && \
    rm -rf node_modules package-lock.json
RUN npm install
RUN npm run build

# Copy the built files to the nginx directory
RUN cp -r /app/dist/* /www

COPY --chown=www:www ./Frontend/nginx.conf /etc/nginx/nginx.conf
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD curl -sSf http://localhost:443 > /dev/null &&  echo "success" || echo "failure"
RUN chown -R www:www /run/nginx

# COPY --chown=www:www ./Frontend/src /www/src

USER www
CMD ["sh", "tools.sh"]
