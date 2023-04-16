# rabbitmq-utils
This package will provide easy connection to rabbitmq server.

## Producer

Following sample code will allow you to send the message to desire queue. 

In **RabbitMQProducer** class **Publisher Confirms** is implemented, So it will tell you weather the message is send to desire location or not.

```python
from rabbitmq_utils.producer import RabbitMQProducer
import json

# DEFINING MESSAGE
message = json.dumps({'hello': 'world'})

# SENDING
rmqp = RabbitMQProducer(
    host='localhost', port=5672, virtual_host='/', 
    username='guest', password='guest', 
    exchange='test_exc', exchane_type='topic'
)
is_sent = rmqp.sendMessage(
    message,
    routing_key
)

# RESULT
if is_sent:
    print('INFO: Message sent.')
else:
    print('ERROR: Unable to send on desire routing key.')
```

## Consumer

**RabbitMQConsumer** class allow you define queue, define exchange and bind queue and exchange using routing key.

Queue and Exchange are consider to be durable. If you are getting some error then remove the existing queue and exchange, before running this code.

Callback function is called when message is received from the rabbitmq server. So define your callback function using following example:

```python
def my_callback_function(ch, method, properties, body):
    # GETTING MESSAGE
    message = body.decode()
    
    # PERFORM YOUR LOGIC HERE
    
    # ACKNOWLEDGE WORK IS DONE
    ch.basic_ack(delivery_tag=method.delivery_tag)
    return None
```

Following sample code will allow you to receive message from rabbitmq server.

```python
from rabbitmq_utils.consumer import RabbitMQConsumer

# STARTING RABBITMQ CONSUMER
rmqc = RabbitMQConsumer(
        host='localhost', port=5672, virtual_host='/', 
        username='guest', password='guest', exchange='test_exc', 
        queue_name='test_que', routing_key='test_key', exchane_type='topic',
    	my_callback_function
)
rmqc.receiveMessage()
```

## Author

**Tahir Rafique**
