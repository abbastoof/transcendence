#! /bin/bash
bin/zookeeper-server-start.sh config/zookeeper.properties > zookeeper.log 2>&1 &
sleep 5
bin/kafka-server-start.sh config/server.properties > kafka.log 2>&1 &
