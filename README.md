# rabbitmq-utils
This package will provide easy connection to rabbitmq server.

## Producer

Following sample code will allow you to send the message to desire queue. 

In **RabbitMQProducer** class **Publisher Confirms** is implemented, So it will tell you weather the message is send to desire location or not.

```python
from rabbitmq_utils.producer import RabbitMQProducer

# INFORMATION
host = 'localhost'
port = 5672
virtual_host = '/'
username = 'guest'
password = 'guest'
exchange = ''
routing_key = 'test'
exchane_type='topic'

# DEFINING MESSAGE
import json
message = json.dumps({'hello': 'world'})

# SENDING
producer = RabbitMQProducer(host, port, virtual_host, username, password, exchange, exchane_type)
is_sent = producer.sendMessage(
    message,
    routing_key
)

# RESULT
if is_sent:
    print('INFO: Message sent.')
else:
    print('ERROR: Unable to send on desire routing key.')
```



