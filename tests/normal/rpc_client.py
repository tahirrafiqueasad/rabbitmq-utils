from rabbitmq_utils.rpc import RPCClient

if __name__ == "__main__":
    # INFORMATION
    host = "localhost"
    port = 5672
    virtual_host = "/"
    username = "guest"
    password = "guest"
    exchange = "test_exc"
    routing_key = "test_key"
    persistent_message = True

    # DEFINING MESSAGE
    import json

    message = json.dumps({"wait_time": 2})

    # SENDING
    client = RPCClient(
        host,
        port,
        virtual_host,
        username,
        password,
        exchange,
        timeout=3,
        persistent_message=persistent_message,
    )
    is_sent, response = client.send_message(message, routing_key, return_response=True)

    # OUTPUT
    print(f"is_sent: {is_sent} \t code: {client.get_code()} \t response: {response}")
