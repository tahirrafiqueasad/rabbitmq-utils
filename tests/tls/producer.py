from rabbitmq_utils.producer import RabbitMQProducer

if __name__ == "__main__":
    # INFORMATION
    host = "localhost"
    port = 5671
    virtual_host = "/"
    username = "guest"
    password = "guest"
    exchange = "test_exc"
    routing_key = "test_key"
    persistent_message = True
    cafile = "docker/certs/ca.crt"
    check_hostname = True

    # DEFINING MESSAGE
    import json

    message = json.dumps({"wait_time": 240})

    # SENDING
    producer = RabbitMQProducer(
        host,
        port,
        virtual_host,
        username,
        password,
        exchange,
        persistent_message=persistent_message,
        cafile=cafile,
        check_hostname=check_hostname,
    )
    is_sent = producer.send_message(message, routing_key)

    # RESULT
    if is_sent:
        print("INFO: Message sent.")
    else:
        print("ERROR: Unable to send on desire routing key.")
