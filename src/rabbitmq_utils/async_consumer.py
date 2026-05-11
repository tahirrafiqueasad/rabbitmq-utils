import asyncio
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
        host: str = "localhost",
        port: str | int = 5672,
        virtualhost: str = "/",
        exchange: str = "main_exchange",
        queue_name: str = "test_queue",
        routing_key: str = "",
        username: str = "guest",
        password: str = "guest",
        exchange_type: str = "topic",
        callback_fun=callback_test,
        prefetch_count: int = 1,
        heartbeat: int = 60,
    ):
        self.host = host
        self.port = port
        self.virtualhost = virtualhost
        self.exchange = exchange
        self.queue_name = queue_name
        self.callback_fun = callback_fun
        self.routing_key = routing_key or queue_name
        self.username = username
        self.password = password
        self.exchange_type = exchange_type
        self.prefetch_count = prefetch_count
        self.heartbeat = heartbeat

        self.connection = None
        self.channel = None

    async def connect(self):
        """Establishes connection and sets up exchange/queue."""
        connection_url = f"amqp://{self.username}:{self.password}@{self.host}:{self.port}/{self.virtualhost}"

        # Setting a heartbeat
        self.connection = await aio_pika.connect_robust(
            connection_url, heartbeat=self.heartbeat
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
            try:
                data = message.body.decode()
                await self.callback_fun(data)
            except Exception as e:
                print(f"Error processing message: {e}")

    async def start_consuming(self):
        """Starts the consumer loop."""
        queue = await self.connect()
        print(f"Waiting for messages in {self.queue_name}. To exit press CTRL+C")

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
