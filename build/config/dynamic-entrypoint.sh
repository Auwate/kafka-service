#!/bin/bash

# Get current IP address
BROKER_IP="$(hostname -i)"
BROKER_PORT="${KAFKA_PORT}"
BROKER_CONTAINER="${KAFKA_CONTAINER_NAME}"

export KAFKA_ADVERTISED_LISTENERS="PLAINTEXT://${BROKER_CONTAINER}:19092,PLAINTEXT_HOST://${BROKER_IP}:${BROKER_PORT}"

exec /opt/kafka/bin/kafka-server-start.sh /opt/kafka/config/server.properties
