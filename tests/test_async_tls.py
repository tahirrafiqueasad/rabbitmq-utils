"""
Pytest tests for async RabbitMQ producer and consumer.
Tests publish a message and verify it is consumed successfully.
"""

import asyncio
import json

import pytest
import pytest_asyncio

from rabbitmq_utils.async_consumer import AsyncRabbitMQConsumer
from rabbitmq_utils.async_producer import AsyncRabbitMQProducer

# Configuration
HOST = "localhost"
PORT = 5671  # TLS port
VIRTUAL_HOST = "/"
USERNAME = "guest"
PASSWORD = "guest"
EXCHANGE = "test_exchange_tls"
ROUTING_KEY = "test.routing.key.tls"
QUEUE_NAME = "test_queue_tls"
CAFILE = "docker/certs/ca.crt"
CHECK_HOSTNAME = True


class MessageCapture:
    """Helper to capture messages from consumer callback."""

    def __init__(self):
        self.received_message = None
        self.callback_called = False

    async def callback(self, body: str):
        """Callback that captures message."""
        self.received_message = body
        self.callback_called = True


@pytest_asyncio.fixture
async def cleanup_queue():
    """Fixture to cleanup the test queue after tests."""
    yield
    # Cleanup: delete the queue after test
    try:
        consumer = AsyncRabbitMQConsumer(
            HOST,
            PORT,
            VIRTUAL_HOST,
            USERNAME,
            PASSWORD,
            QUEUE_NAME,
            ROUTING_KEY,
            EXCHANGE,
            cafile=CAFILE,
            check_hostname=CHECK_HOSTNAME,
        )
        queue = await consumer.connect()
        await queue.delete()
        await consumer.connection.close()
    except:
        pass  # Ignore cleanup errors


@pytest.mark.asyncio
async def test_publish_and_consume_message(cleanup_queue):
    """
    Test that a message can be published and consumed asynchronously.

    Steps:
    1. Create and connect consumer to set up the queue.
    2. Publish the message using producer.
    3. Consume the message using consumer.
    """
    test_message = json.dumps({"test": "data", "value": 42})
    message_capture = MessageCapture()

    # Step 1: Create and connect consumer to set up the queue
    consumer = AsyncRabbitMQConsumer(
        HOST,
        PORT,
        VIRTUAL_HOST,
        USERNAME,
        PASSWORD,
        QUEUE_NAME,
        ROUTING_KEY,
        EXCHANGE,
        callback_fun=message_capture.callback,
        cafile=CAFILE,
        check_hostname=CHECK_HOSTNAME,
    )
    await consumer.connect()
    await consumer.connection.close()

    # Step 2: Publish the message using producer
    producer = AsyncRabbitMQProducer(
        HOST,
        PORT,
        VIRTUAL_HOST,
        USERNAME,
        PASSWORD,
        EXCHANGE,
        persistent_message=True,
        cafile=CAFILE,
        check_hostname=CHECK_HOSTNAME,
    )
    is_published, exc = await producer.publish_message(
        test_message,
        ROUTING_KEY,
        close_connection=True,
        return_exception=True,
    )

    assert is_published, f"Message should be published successfully. Error: {exc}"

    # Step 3: Consume the message using consumer
    consumer = AsyncRabbitMQConsumer(
        HOST,
        PORT,
        VIRTUAL_HOST,
        USERNAME,
        PASSWORD,
        QUEUE_NAME,
        ROUTING_KEY,
        EXCHANGE,
        callback_fun=message_capture.callback,
        cafile=CAFILE,
        check_hostname=CHECK_HOSTNAME,
    )

    try:
        await asyncio.wait_for(
            consumer.start_consuming(),
            timeout=2.0,
        )
    except asyncio.TimeoutError:
        pass

    # Assert - Message consumed successfully
    assert message_capture.callback_called, "Callback should have been called"
    assert message_capture.received_message is not None, "Message should be received"
    assert (
        message_capture.received_message == test_message
    ), "Message content should match"
