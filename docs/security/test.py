import asyncio
import json
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

async def collectMetrics():

    print("Creating consumer")

    aio_consumer = AIOKafkaConsumer(
            "event_logs",
            bootstrap_servers='localhost:29092',
            auto_offset_reset="earliest",
            # security_protocol='SASL_PLAINTEXT',
            # sasl_mechanism='SCRAM-SHA-512',
            # sasl_plain_username='test-user',
            # sasl_plain_password='password'
    )

    print("Awaiting consumer")

    await aio_consumer.start()

    print("Creating producer")

    aio_producer = AIOKafkaProducer(
            bootstrap_servers='localhost:29092',
            # security_protocol='SASL_PLAINTEXT',
            # sasl_mechanism='SCRAM-SHA-512',
            # sasl_plain_username='test-user',
            # sasl_plain_password='password'
    )

    print("Awaiting producer")

    await aio_producer.start()

    try:
    
        print("Trying to send")

        await aio_producer.send("event_logs", json.dumps("hello").encode())
            #message_data = consumer.poll(timeout_ms=300, max_records=100)
            #if message_data:
            #    for _, consumer_records in message_data.items():
            #        for record in consumer_records:
            #            data.append({"timestamp": record.timestamp, "value": record.value})

        print("Trying to consume")

        async for n in aio_consumer:
            print(n)
            value = json.loads(n.value.decode("utf-8"))
            print(f"The message pulled from Kafka contained {value}")
            break

    except Exception as exc:  # pylint: disable=W0718
        raise exc

    finally:
        await aio_consumer.stop()
        await aio_producer.stop()

if __name__ == "__main__":
    asyncio.run(collectMetrics())
