"""
Pytest tests for blocking (sync) RabbitMQ producer and consumer.
Tests publish a message and verify it is consumed successfully.
"""

import json

import pytest

from rabbitmq_utils.consumer import RabbitMQConsumer
from rabbitmq_utils.producer import RabbitMQProducer

# Configuration
HOST = "localhost"
PORT = 5672
VIRTUAL_HOST = "/"
USERNAME = "guest"
PASSWORD = "guest"
EXCHANGE = "test_exchange"
ROUTING_KEY = "test.routing.key"
QUEUE_NAME = "test_queue"


class MessageCapture:
    """Helper to capture messages from consumer callback."""

    def __init__(self):
        self.received_message = None
        self.callback_called = False

    def callback(self, ch, method, properties, body):
        """Callback that captures message and stops consuming."""
        self.received_message = body.decode()
        self.callback_called = True
        ch.basic_ack(delivery_tag=method.delivery_tag)
        # Stop consuming after first message
        ch.stop_consuming()


@pytest.fixture
def cleanup_queue():
    """Fixture to cleanup the test queue after tests."""
    yield
    # Cleanup: delete the queue after test
    try:
        consumer = RabbitMQConsumer(
            HOST,
            PORT,
            VIRTUAL_HOST,
            USERNAME,
            PASSWORD,
            QUEUE_NAME,
            ROUTING_KEY,
            EXCHANGE,
        )
        consumer.make_connection()
        consumer.channel.queue_delete(queue=QUEUE_NAME)
    except:
        pass  # Ignore cleanup errors


def test_publish_and_consume_message(cleanup_queue):
    """
    Test that a message can be published and consumed.

    Steps:
    1. Create a queue.
    2. Publish the message.
    3. Consume the message.
    """
    # Defining the queue first
    # Act - Consume message
    message_capture = MessageCapture()
    consumer = RabbitMQConsumer(
        HOST,
        PORT,
        VIRTUAL_HOST,
        USERNAME,
        PASSWORD,
        QUEUE_NAME,
        ROUTING_KEY,
        EXCHANGE,
        callback_fun=message_capture.callback,
    )
    consumer.make_connection()

    # Arrange
    test_message = json.dumps({"test": "data", "value": 42})

    # Act - Publish message
    producer = RabbitMQProducer(
        HOST,
        PORT,
        VIRTUAL_HOST,
        USERNAME,
        PASSWORD,
        EXCHANGE,
        persistent_message=True,
    )
    is_published, exc = producer.send_message(
        test_message, ROUTING_KEY, return_exception=True
    )

    # Assert - Message published successfully
    assert is_published, "Message should be published successfully"

    consumer.start_reveiving()

    # Assert - Message consumed successfully
    assert message_capture.callback_called, "Callback should have been called"
    assert message_capture.received_message is not None, "Message should be received"
    assert (
        message_capture.received_message == test_message
    ), "Message content should match"
