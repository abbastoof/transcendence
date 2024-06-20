FROM alpine:3.20

RUN apk add --no-cache erlang openssl bash

# Set environment variable for RabbitMQ installation directory
RUN addgroup -S rabbitmq && adduser -S rabbitmq -G rabbitmq
ENV RABBITMQ_HOME=/usr/local/bin/rabbitmq_server-3.13.3
RUN mkdir -p $RABBITMQ_HOME && chown -R rabbitmq:rabbitmq /usr/local/bin/ && \
    # Download and install RabbitMQ
    wget https://github.com/rabbitmq/rabbitmq-server/releases/download/v3.13.3/rabbitmq-server-generic-unix-3.13.3.tar.xz && \
    tar xvf rabbitmq-server-generic-unix-3.13.3.tar.xz -C /usr/local/bin/ && \
    rm rabbitmq-server-generic-unix-3.13.3.tar.xz

    # Add RabbitMQ binaries to PATH
ENV PATH=$PATH:$RABBITMQ_HOME/sbin
USER root
RUN chown -R rabbitmq:rabbitmq $RABBITMQ_HOME
USER rabbitmq
RUN rabbitmq-plugins enable rabbitmq_management
# Expose ports used by RabbitMQ
EXPOSE 5672 15672

# Add HEALTHCHECK instruction
HEALTHCHECK --interval=30s --timeout=5s CMD rabbitmqctl node_health_check || exit 1

# Run RabbitMQ server
CMD ["rabbitmq-server", "detached"]
