"""
Pytest tests for blocking (sync) RabbitMQ rpc client and server.
Tests publish a message and verify it is consumed successfully.
"""

import pika
import json
import pytest
from rabbitmq_utils.rpc import RPCClient, RPCServer

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
        message = body.decode()
        self.received_message = message
        self.callback_called = True

        # Updating data value
        data = json.loads(message)
        data["value"] += 5
        response = json.dumps(data)

        # Sending back message
        ch.basic_publish(
            exchange="",
            routing_key=properties.reply_to,
            properties=pika.BasicProperties(correlation_id=properties.correlation_id),
            body=str(response),
        )

        ch.basic_ack(delivery_tag=method.delivery_tag)
        # Stop consuming after first message
        ch.stop_consuming()


@pytest.fixture
def cleanup_queue():
    """Fixture to cleanup the test queue after tests."""
    yield
    # Cleanup: delete the queue after test
    try:
        consumer = RPCServer(
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


def test_rpc_client_server(cleanup_queue):
    """
    Test that perform the following steps.

    Steps:
    1. Create a queue.
    2. Message publish by client.
    3. Message consume by consumer.
    4. Message receive by the client.
    """
    # Defining the queue first
    # Act - Consume message
    message_capture = MessageCapture()
    server = RPCServer(
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
    server.make_connection()

    # Arrange
    test_message = json.dumps({"test": "data", "value": 40})

    # Act - Publish message
    client = RPCClient(
        HOST,
        PORT,
        VIRTUAL_HOST,
        USERNAME,
        PASSWORD,
        EXCHANGE,
        persistent_message=True,
    )
    is_published = client.send_message(test_message, ROUTING_KEY, return_response=False)

    # Assert - Message published successfully
    assert is_published, "Message should be published successfully"

    # Conuming the message
    server.start_reveiving()

    # Assert - Message consumed successfully
    assert message_capture.callback_called, "Callback should have been called"
    assert message_capture.received_message is not None, "Message should be received"
    assert (
        message_capture.received_message == test_message
    ), "Message content should match"

    # Validating return value on client side
    response = client.receive_response()
    data = json.loads(response)
    assert data["value"] == 45, "Incorrect value is received from server."
