FROM alpine:3.20

RUN apk add --no-cache erlang openssl

# Set environment variable for RabbitMQ installation directory
ENV RABBITMQ_HOME=/usr/local/bin/rabbitmq_server-3.13.3

# Download and install RabbitMQ
RUN wget https://github.com/rabbitmq/rabbitmq-server/releases/download/v3.13.3/rabbitmq-server-generic-unix-3.13.3.tar.xz && \
    tar xvf rabbitmq-server-generic-unix-3.13.3.tar.xz -C /usr/local/bin/ && \
    rm rabbitmq-server-generic-unix-3.13.3.tar.xz

# Add RabbitMQ binaries to PATH
ENV PATH=$PATH:$RABBITMQ_HOME/sbin

# Expose ports used by RabbitMQ
EXPOSE 5672 15672

# Run RabbitMQ server
CMD ["rabbitmq-server", "detached"]