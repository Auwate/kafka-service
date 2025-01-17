# Code Documentation

This module provides sample code that developers can use to integrate Kafka into their project. The code samples use `JSON` and `AIOKafka` to serialize and send their data, respectively.

## Why AIOKafka and not kafka-python-ng?

`AIOKafka` is the asynchronous alternative to `kafka-python-ng` (or the legacy version `kafka-python`). Both will perform at similar levels and have an almost identical API. However, a major issue with `kafka-python-ng` was how it handled concurrent processing with consumers in consumer groups. Specifically, part of the architectural design of consumer groups was to have each consumer in a consumer group be part of their own dedicated thread or process. While this works for many applications, the modern approach for Python projects is to use async/await. In addition, if the number of consumers goes too high, it may lead to memory consumption issues, as threads on Python are considerably bulky.

Now, if the current project you are working on uses threads, thread pools, or a multi-process approach, then you may find `kafka-python-ng` easier to integrate into your application. It's the more traditional way, and was built to mimic the architectural design seen in Java. In that case, please keep in mind that consumer groups will not work correctly unless you place each consumer of a consumer group in their own thread, or else you will find that application freezes. If you're only using ONE consumer, this will not be a problem as it's running on the main thread.

# sample_class.py

This showcases a possible strongly-coupled class that has inheritance, dependencies, etc. This idea is that JSON encoder will likely not be able to serialize it on it's own, hence requiring us to create our own, called `sample_json_serializer.py`

# sample_json_serializer.py

This holds a sample JSON serializer that allows us to serialize classes and other objects. It looks ironically not complex, but it implements the `default` method, which the base JSON encoder will use if it finds something it cannot encode.

# sample_consumer.py

This shows some usages of the `AIOKafkaConsumer` class, creating multiple async coroutines to showcase multi-consumer setups. It uses the `async for` loop, which is a streamlined alternative to the `.getone()` or `.getmany()` async functions. In addition, it shows how the return object is of type ConsumerRecord.

# sample_producer.py

This shows usage of the `AIOKafkaProducer` class, creating a single producer that randomly creates a class from `sample_class.py`. In addition, it shows how to use the `json` module with a implemented version of `JSONEncoder`.
