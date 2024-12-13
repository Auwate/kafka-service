FROM apache/kafka:latest

WORKDIR /opt/kafka

USER root

COPY dynamic-entrypoint.sh /opt/kafka/dynamic-entrypoint.sh
RUN chmod +x /opt/kafka/dynamic-entrypoint.sh

USER kafka

ENTRYPOINT [ "/opt/kafka/dynamic-entrypoint.sh" ]

CMD [ "/opt/kafka/bin/kafka-server-start.sh", "/opt/kafka/config/server.properties" ]