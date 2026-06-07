"""
Pytest tests for TLS-enabled blocking (sync) RabbitMQ producer and consumer.
Tests publish a message over TLS and verify it is consumed successfully.
"""

import json

import pytest

from rabbitmq_utils.consumer import RabbitMQConsumer
from rabbitmq_utils.producer import RabbitMQProducer

# TLS Configuration
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

    def callback(self, ch, method, properties, body):
        """Callback that captures message and stops consuming."""
        self.received_message = body.decode()
        self.callback_called = True
        ch.basic_ack(delivery_tag=method.delivery_tag)
        # Stop consuming after first message
        ch.stop_consuming()


@pytest.fixture
def cleanup_queue_tls():
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
            cafile=CAFILE,
            check_hostname=CHECK_HOSTNAME,
        )
        consumer.make_connection()
        consumer.channel.queue_delete(queue=QUEUE_NAME)
    except:
        pass  # Ignore cleanup errors


def test_publish_and_consume_message_tls(cleanup_queue_tls):
    """
    Test that a message can be published and consumed over TLS.

    Steps:
    1. Create a queue with TLS.
    2. Publish the message over TLS.
    3. Consume the message over TLS.
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
        cafile=CAFILE,
        check_hostname=CHECK_HOSTNAME,
    )
    consumer.make_connection()

    # Arrange
    test_message = json.dumps({"test": "tls_data", "value": 123})

    # Act - Publish message
    producer = RabbitMQProducer(
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
    is_published, exc = producer.send_message(
        test_message, ROUTING_KEY, return_exception=True
    )

    # Assert - Message published successfully
    assert is_published, "Message should be published successfully over TLS"

    consumer.start_reveiving()

    # Assert - Message consumed successfully
    assert message_capture.callback_called, "Callback should have been called"
    assert message_capture.received_message is not None, "Message should be received"
    assert (
        message_capture.received_message == test_message
    ), "Message content should match"
