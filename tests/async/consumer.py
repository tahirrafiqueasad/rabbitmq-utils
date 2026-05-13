import asyncio

from rabbitmq_utils import AsyncRabbitMQConsumer

if __name__ == "__main__":
    # INFORMATION
    host = "localhost"
    port = 5672
    virtual_host = "/"
    username = "guest"
    password = "guest"
    exchange = "test_exc"
    routing_key = "test_key"
    queue_name = "test_que"

    # RECEIVING
    consumer = AsyncRabbitMQConsumer(
        host,
        port,
        virtual_host,
        username,
        password,
        queue_name,
        routing_key,
        exchange,
    )

    try:
        print("Starting consumer.")
        asyncio.run(consumer.start_consuming())
    except KeyboardInterrupt:
        print("Consumer stopped.")
