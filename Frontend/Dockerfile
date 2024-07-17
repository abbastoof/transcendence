# Base stage
FROM alpine:3.20 AS frontend

# Install necessary packages
RUN apk update && apk add --no-cache nginx openrc openssl openssh curl bash nodejs npm

# Set up the application directory
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

# Copy shared files
COPY --chown=www:www ./Frontend/tools.sh /app/tools.sh
RUN chmod +x /app/tools.sh

# Copy application files
COPY --chown=www:www ./Frontend/package.json /app/package.json
COPY --chown=www:www ./Frontend/package-lock.json /app/package-lock.json
COPY --chown=www:www ./Frontend/vite.config.js /app/vite.config.js

# Set the working directory
# WORKDIR /app

# Copy your frontend application files
#COPY --chown=www:www ./Frontend/src /www/
WORKDIR /app
COPY --chown=www:www ./Frontend/src /app/src
RUN chown -R www:www /app

# Install npm dependencies
RUN npm cache clean --force && \
    rm -rf node_modules package-lock.json && \
    npm install

# Development stage
FROM frontend AS development

# Expose port for Vite development server
EXPOSE 3000

# Development command
CMD ["npm", "run", "dev"]

# Production stage
FROM frontend AS production

# Build the project
RUN npm run build

# Copy the built files to the nginx directory
RUN cp -r /app/dist/* /www

# Copy nginx configuration
COPY --chown=www:www ./Frontend/nginx.conf /etc/nginx/nginx.conf
RUN chown -R www:www /run/nginx

# Expose port for Nginx server
EXPOSE 443

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD curl -sSf http://localhost:443 > /dev/null && echo "success" || echo "failure"

# Set up the final command
USER www
CMD ["sh", "/app/tools.sh"]
