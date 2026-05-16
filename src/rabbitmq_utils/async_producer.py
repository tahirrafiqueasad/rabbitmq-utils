"""
Author:		 Muhammad Tahir Rafique
Date:		 2026-05-12 20:14:28
Project:	 rabbitmq-utils
Description: Provide function to send the message to rabbitmq exchange.
"""

import asyncio
import ssl
import aio_pika


class AsyncRabbitMQProducer:
    def __init__(
        self,
        host: str,
        port: str,
        virtual_host: str,
        username: str,
        password: str,
        exchange: str = "",
        exchange_type: str = "topic",
        persistent_message: bool = False,
        cafile: str | None = None,
        check_hostname: bool = True,
    ):
        self.host = host
        self.port = port
        self.virtual_host = virtual_host
        self.username = username
        self.password = password
        self.exchange_name = exchange
        self.exchange_type = exchange_type
        self.cafile = cafile
        self.check_hostname = check_hostname

        self.connection = None
        self.channel = None
        self.exchange = None

        # Defining delivery method
        self.delivery_mode = aio_pika.DeliveryMode.NOT_PERSISTENT
        if persistent_message:
            self.delivery_mode = aio_pika.DeliveryMode.PERSISTENT

        # Defining schema
        if cafile:
            self.schema = "amqps"
        else:
            self.schema = "amqp"

        # Internal variables
        self._is_sent = None
        self._exception = None
        return None

    def _on_message_returned(self, sender, message):
        self._is_sent = False
        self._exception = Exception("Unable to route message to queue.")
        return None

    async def connect(self):
        """Initializes the connection and declares the exchange."""
        connection_url = f"{self.schema}://{self.username}:{self.password}@{self.host}:{self.port}/{self.virtual_host}"

        ssl_context = None
        if self.cafile:
            # Create a secure SSL context
            ssl_context = ssl.create_default_context(cafile=self.cafile)
            ssl_context.check_hostname = self.check_hostname

        # connect_robust handles reconnection automatically if the server blips
        self.connection = await aio_pika.connect_robust(
            connection_url, ssl_context=ssl_context
        )
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
        return_exception: bool = False,
    ):
        """Publish the message to provided routing key.

        Args:
            message (str): Message that will be publised.
            routing_key (str): Route on which message will be publish.
            close_connection (bool, optional): After the publish close the connection. Defaults to True.
            confirm_wait (int, optional): ms wait to check message is delivered to queue (not recomended). Defaults to 0.

        Returns:
            is_sent: True if send to exchange
            exc: Exception | None
        """
        try:
            self._is_sent = True
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

            # Waiting if requred
            if confirm_wait:
                await asyncio.sleep(confirm_wait / 1000)

            # Defining variables
            is_sent = self._is_sent
            error = self._exception
        except Exception as e:
            is_sent = False
            error = e
        finally:
            # Checking connection
            if close_connection:
                await self.close()
        # If exception is required
        if return_exception:
            return is_sent, error
        # Otherwise just return the status.
        return is_sent


# Example Usage
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

    # Simulate sending a few tasks
    for i in range(5):
        data = "Ho how are you"
        is_sent, exc = await producer.publish_message(
            data,
            "test_key",
            close_connection=False,
            confirm_wait=500,
            return_exception=True,
        )
        await asyncio.sleep(1)  # Small delay between publishes

    await producer.close()


if __name__ == "__main__":
    asyncio.run(main())
