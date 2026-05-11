import asyncio
import aio_pika


class AsyncRabbitMQProducer:
    def __init__(
        self,
        host="localhost",
        port=5672,
        virtual_host="/",
        username="guest",
        password="guest",
        exchange_name="test_exc",
        exchange_type="topic",
        persistent_message: bool = False,
    ):
        self.host = host
        self.port = port
        self.virtual_host = virtual_host
        self.username = username
        self.password = password
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type

        self.connection = None
        self.channel = None
        self.exchange = None

        # Defining delivery method
        self.delivery_mode = aio_pika.DeliveryMode.NOT_PERSISTENT
        if persistent_message:
            self.delivery_mode = aio_pika.DeliveryMode.PERSISTENT

        # Internal variables
        self._is_send = None
        self._exception = None
        return None

    def _on_message_returned(self, sender, message):
        self._is_send = False
        self._exception = Exception("Unable to route message to queue.")
        return None

    async def connect(self):
        """Initializes the connection and declares the exchange."""
        connection_url = f"amqp://{self.username}:{self.password}@{self.host}:{self.port}/{self.virtual_host}"

        # connect_robust handles reconnection automatically if the server blips
        self.connection = await aio_pika.connect_robust(connection_url)
        self.channel = await self.connection.channel()

        # 1. Register the return callback to catch unroutable messages
        self.channel.return_callbacks.add(self._on_message_returned)

        # We declare the exchange to ensure it exists before we try to publish
        self.exchange = await self.channel.declare_exchange(
            name=self.exchange_name, type=self.exchange_type, durable=True
        )
        return None

    async def close(self):
        """Gracefully closes the connection."""
        if self.connection:
            await self.connection.close()
        return None

    async def publish_message(
        self,
        message: str,
        routing_key: str,
        close_connection: bool = True,
        confirm_wait: int = 0,
    ):
        """Publish the message to provided routing key.

        Args:
            message (str): Message that will be publised.
            routing_key (str): Route on which message will be publish.
            close_connection (bool, optional): After the publish close the connection. Defaults to True.
            confirm_wait (int, optional): ms wait to check message is delivered to queue (not recomended). Defaults to 0.

        Returns:
            is_send: True if send to exchange
            exc: Exception | None
        """
        try:
            self._is_send = None
            self._exception = None
            if not self.exchange:
                await self.connect()

            # Publishing message
            body = message.encode()
            message = aio_pika.Message(
                body=body,
            )
            await self.exchange.publish(
                message, routing_key=routing_key, mandatory=True
            )

            # Checking connection
            if close_connection:
                await self.close()

            # Waiting if requred
            if confirm_wait:
                await asyncio.sleep(confirm_wait / 1000)

            # Defining variables
            is_send = self._is_send
            error = self._exception
        except Exception as e:
            is_send = False
            error = e
        return is_send, error


# Example Usage
async def main():
    # Defining producer class
    producer = AsyncRabbitMQProducer()

    # Simulate sending a few tasks
    for i in range(5):
        data = "Ho how are you"
        is_send, exc = await producer.publish_message(
            data, "test_key", close_connection=False, confirm_wait=500
        )
        await asyncio.sleep(1)  # Small delay between publishes

    await producer.close()


if __name__ == "__main__":
    asyncio.run(main())
