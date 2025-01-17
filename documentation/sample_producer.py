"""
A sample producer that uses JSON serialization
"""

import json
import asyncio
import random
from aiokafka import AIOKafkaProducer
from sample_class import SampleClass, DependencyClass1, DependencyClass2
from sample_json_serializer import ComplexEncoder

async def produce():
    """
    Sample producer
    """
    producer = AIOKafkaProducer(
        bootstrap_servers=[
            "170.39.8.67:29092",
            "170.39.8.67:29093",
            "170.39.8.68:39092",
            "170.39.8.68:39093",
            "170.39.8.69:49092",
            "170.39.8.69:49093",
        ],
    )

    try:

        await producer.start() # Required

        while True:

            # Randomly choose a class to send
            choice: int = random.randint(0, 2)

            if choice == 0:
                message = SampleClass()
            elif choice == 1:
                message = DependencyClass1()
            else:
                message = DependencyClass2()

            # Send with the JSON encoder
            await producer.send_and_wait(
                "event_logs", value=json.dumps(message, cls=ComplexEncoder).encode("utf-8")
            )

    finally:
        await producer.stop()


async def main():
    tasks = [produce()]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
