"""
A sample consumer that decodes from JSON
"""

import json
import asyncio
from aiokafka import AIOKafkaConsumer

async def consume(index: int):
    """
    Sample consumer
    """
    consumer = AIOKafkaConsumer(
        bootstrap_servers=[
            "kafka-server1.amlight.net:29092",
            "kafka-server1.amlight.net:29093",
            "kafka-server2.amlight.net:39092",
            "kafka-server2.amlight.net:39093",
            "kafka-server3.amlight.net:49092",
            "kafka-server3.amlight.net:49093",
        ],
        group_id="test_group",
        enable_auto_commit=True,
        auto_offset_reset="earliest",
    )

    await consumer.start() # Required

    consumer.subscribe(topics=["event_logs"]) # Optional: For dynamically assigning topics

    try:
        while True:
            async for msg in consumer:
                # Data comes in as a ConsumerRecord
                msg.value = json.loads(msg.value.decode("utf-8"))

                print(
                    f"\n\nCONSUMER {index}\n",
                    f"Value: {msg.value}\n",
                    f"Header: {msg.headers}\n",
                    f"Key: {msg.key}\n",
                    f"Offset: {msg.offset}\n",
                )
                # Simulate "processing"
                await asyncio.sleep(0.005)
    except Exception as exc:  # pylint: disable=W0718
        # Do something
        print(exc)
    finally:
        await consumer.stop()


async def main():
    tasks = [consume(i + 1) for i in range(4)]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
