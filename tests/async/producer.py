import json
import asyncio

from rabbitmq_utils import AsyncRabbitMQProducer


async def main():
    # Defining producer class
    producer = AsyncRabbitMQProducer(
        host="localhost",
        port="5672",
        virtual_host="/",
        username="guest",
        password="guest",
        exchange="test_exc",
    )

    message = json.dumps({"wait_time": 5})

    # Simulate sending a few tasks
    is_sent, exc = await producer.publish_message(
        message,
        "test_key",
        close_connection=True,
        confirm_wait=0,
        return_exception=True,
    )
    # Result
    if is_sent:
        print("INFO: Message sent.")
    else:
        print("ERROR: Unable to send on desire routing key.")


if __name__ == "__main__":
    asyncio.run(main())
