#!/bin/bash

# Start Zookeeper in the foreground and redirect logs
bin/zookeeper-server-start.sh config/zookeeper.properties > zookeeper.log 2>&1 &

# Wait for Zookeeper to start
sleep 10

# Start Kafka in the foreground and redirect logs
bin/kafka-server-start.sh config/server.properties > kafka.log 2>&1 &
