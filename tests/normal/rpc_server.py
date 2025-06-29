from rabbitmq_utils.rpc import RPCServer

if __name__ == "__main__":
    # INFORMATION
    host = "localhost"
    port = 5672
    virtual_host = "/"
    username = "guest"
    password = "guest"
    exchange = "test_exc"
    routing_key = "test_key"
    queue_name = "test_que"

    # RECEIVING
    server = RPCServer(
        host,
        port,
        virtual_host,
        username,
        password,
        queue_name,
        routing_key,
        exchange,
    )
    server.receive_message()
