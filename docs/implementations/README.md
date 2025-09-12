# implementations/

Contains examples for implementations using `aiokafka`

## sample_class.py

This showcases a possible strongly-coupled class that has inheritance, dependencies, etc. This idea is that JSON encoder will likely not be able to serialize it on it's own, hence requiring us to create our own, called `sample_json_serializer.py`

## sample_json_serializer.py

This holds a sample JSON serializer that allows us to serialize classes and other objects. It looks ironically not complex, but it implements the `default` method, which the base JSON encoder will use if it finds something it cannot encode.

## sample_consumer.py

This shows some usages of the `AIOKafkaConsumer` class, creating multiple async coroutines to showcase multi-consumer setups. It uses the `async for` loop, which is a streamlined alternative to the `.getone()` or `.getmany()` async functions. In addition, it shows how the return object is of type ConsumerRecord.

## sample_producer.py

This shows usage of the `AIOKafkaProducer` class, creating a single producer that randomly creates a class from `sample_class.py`. In addition, it shows how to use the `json` module with a implemented version of `JSONEncoder`.