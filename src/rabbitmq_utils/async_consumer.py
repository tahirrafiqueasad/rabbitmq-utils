"""
Author:		 Muhammad Tahir Rafique
Date:		 2026-05-12 19:43:56
Project:	 rabbitmq-utils
Description: Provide function to start the rabbitmq consumer.
"""

import asyncio
import ssl

import aio_pika
from aio_pika.abc import AbstractIncomingMessage


async def callback_test(message):
    # Printing message
    print("==================================")
    print(f"INFO: Received Message: \n\n{message}\n")

    # Performing test logic
    try:
        import json

        wait_sec = json.loads(message)["wait_time"]
        print(f"INFO: Wating for {wait_sec} seconds.")
        for sec in range(wait_sec):
            await asyncio.sleep(1)
            print(f"Remaining Seconds: {wait_sec - sec} / {wait_sec}")
        print("INFO: Done waiting.")
    except:
        pass

    print("INFO: Acknowledgment Done.")
    print("==================================")
    print("\n\n")
    return None


class AsyncRabbitMQConsumer:
    def __init__(
        self,
        host: str,
        port: str,
        virtual_host: str,
        username: str,
        password: str,
        queue_name: str,
        routing_key: str = "",
        exchange: str = "",
        exchange_type: str = "topic",
        callback_fun=callback_test,
        prefetch_count: int = 1,
        max_priority: int | None = None,
        cafile: str | None = None,
        check_hostname: bool = True,
        heartbeat: int = 180,
    ):
        self.host = host
        self.port = port
        self.virtual_host = virtual_host
        self.exchange = exchange
        self.queue_name = queue_name
        self.callback_fun = callback_fun
        self.routing_key = routing_key or queue_name
        self.username = username
        self.password = password
        self.exchange_type = exchange_type
        self.prefetch_count = prefetch_count
        self.heartbeat = heartbeat
        self.cafile = cafile
        self.check_hostname = check_hostname

        # Defining schema
        if cafile:
            self.schema = "amqps"
        else:
            self.schema = "amqp"

        # State variables
        self.connection = None
        self.channel = None
        return None

    async def connect(self):
        """Establishes connection and sets up exchange/queue."""
        connection_url = f"{self.schema}://{self.username}:{self.password}@{self.host}:{self.port}/{self.virtual_host}"

        ssl_context = None
        if self.cafile:
            # Create a secure SSL context
            ssl_context = ssl.create_default_context(cafile=self.cafile)
            ssl_context.check_hostname = self.check_hostname

        # Setting a heartbeat
        self.connection = await aio_pika.connect_robust(
            connection_url, heartbeat=self.heartbeat, ssl_context=ssl_context
        )
        self.channel = await self.connection.channel()

        # Setting prefetch
        await self.channel.set_qos(prefetch_count=self.prefetch_count)

        # Declare the exchange
        exchange = await self.channel.declare_exchange(
            name=self.exchange, type=self.exchange_type, durable=True
        )

        # Declare the queue
        queue = await self.channel.declare_queue(self.queue_name, durable=True)

        # Bind queue to exchange
        await queue.bind(exchange, routing_key=self.routing_key)
        return queue

    async def process_message(self, message: AbstractIncomingMessage):
        """The core logic to call the external method."""
        async with message.process():
            data = message.body.decode()
            await self.callback_fun(data)
        return None

    async def start_consuming(self):
        """Starts the consumer loop."""
        queue = await self.connect()
        await queue.consume(self.process_message)

        # Keep the loop running
        try:
            await asyncio.Future()
        finally:
            await self.connection.close()


if __name__ == "__main__":
    consumer = AsyncRabbitMQConsumer(queue_name="api_tasks")

    try:
        asyncio.run(consumer.start_consuming())
    except KeyboardInterrupt:
        print("Consumer stopped.")
