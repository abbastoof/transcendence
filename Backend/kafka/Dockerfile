FROM alpine:3.20

ENV SCALA_VERSION=2.13
ENV KAFKA_VERSION=3.7.0
ENV KAFKA_HOME=/opt/kafka

RUN apk update && apk add openjdk21-jre-headless wget bash jq curl tar && \
rm -rf /var/lib/apt/lists/*

RUN wget -qO- https://downloads.apache.org/kafka/${KAFKA_VERSION}/kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz | tar xz -C /opt

RUN mv /opt/kafka_${SCALA_VERSION}-${KAFKA_VERSION} ${KAFKA_HOME}

ENV PATH="${PATH}:${KAFKA_HOME}/bin"

RUN mkdir -p /var/lib/kafka/data /var/lib/kafka/logs


COPY Backend/kafka/config/server.properties ${KAFKA_HOME}/config/

EXPOSE 9092 2181

WORKDIR ${KAFKA_HOME}

COPY Backend/kafka/start_kafka.sh ${KAFKA_HOME}/

# Make script executable
RUN chmod +x ${KAFKA_HOME}/start_kafka.sh

RUN bin/zookeeper-server-start.sh config/zookeeper.properties

# Start Zookeeper and Kafka
CMD ["./start_kafka.sh"]

