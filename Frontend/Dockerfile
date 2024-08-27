# Frontend stage
FROM alpine:3.20 AS frontend

# Install necessary packages
RUN apk update && apk add --no-cache nginx openrc openssl openssh curl bash nodejs npm

# Set up the application directory
RUN addgroup -g 1000 www && adduser -D -u 1000 -G www www && \
    mkdir -p /www && \
    mkdir -p /www/avatars && chown -R www:www /www/avatars && chmod 755 /www/avatars && \
    chown -R www:www /var/lib/nginx && \
    chown -R www:www /var/lib/nginx/logs/ && \
    chown -R www:www /www && \
    mkdir -p /etc/nginx/ssl && \
    chown -R www:www /etc/nginx/ssl && \
    chown -R www:www /etc/nginx

# Set working directory
WORKDIR /app

# Copy application files
COPY --chown=www:www ./Frontend/package.json /app/package.json
COPY --chown=www:www ./Frontend/package-lock.json /app/package-lock.json
COPY --chown=www:www ./Frontend/vite.config.js /app/vite.config.js
COPY --chown=www:www ./Frontend/src /app/src
COPY --chown=www:www ./Frontend/src /www/
COPY --chown=www:www ./Frontend/src/assets/images/default.jpg /www/avatars/
COPY --chown=www:www ./Frontend/tools.sh /app/tools.sh

# Install npm dependencies
RUN npm cache clean --force && \
    rm -rf node_modules && \
    npm install && \
    npm cache verify    

# Development stage
FROM frontend AS development

# Copy Nginx configuration for development
COPY --chown=www:www ./Frontend/nginx.conf.dev /etc/nginx/nginx.conf

# Expose port for Vite development server
EXPOSE 3000

# Run Vite and Nginx
CMD ["sh", "/app/tools.sh"]

# Production stage
FROM frontend AS production

# Build the project
RUN npm run build

# Copy the built files to the Nginx directory
RUN cp -r /app/dist/* /www

# Copy Nginx configuration for production
COPY --chown=www:www ./Frontend/nginx.conf /etc/nginx/nginx.conf

# Generate self-signed SSL certificates
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/nginx/ssl/nginx-selfsigned.key \
-out /etc/nginx/ssl/nginx-selfsigned.crt -subj \
"/C=FI/ST=UUSIMAA/L=HELSINKI/O=HIVE/OU=HIVE/CN=localhost"

# Fix permissions
RUN chmod 600 /etc/nginx/ssl/nginx-selfsigned.key /etc/nginx/ssl/nginx-selfsigned.crt && \
    chown -R www:www /var/lib/nginx/logs/ /run/nginx /etc/nginx/ssl

# Expose port for Nginx server
EXPOSE 443

# Set up the final command
USER www
HEALTHCHECK --interval=30s --timeout=2s --start-period=5s --retries=3 CMD curl -sSf https://localhost/ > /dev/null &&  echo "success" || echo "failure"

CMD ["sh", "/app/tools.sh"]
