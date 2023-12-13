# rabbitmq-utils
This package will provide easy connection to rabbitmq server.

## Producer

Following sample code will allow you to send the message to desire queue. 

In **RabbitMQProducer** class **Publisher Confirms** is implemented, So it will tell you weather the message is send to desire location or not.

**Note: In order to use default exchange, use "" as exchange name. When using the default exchange then routing key will be the name of queue.**

In order to make message persistent use **persistent_message=True**. This will increase the disk size as well as latency. The message will be recovered even after the rabbitmq server is restarted. 

If you have priority base queue then you can pass **priority=(some int)** in **sendMessage**.

```python
from rabbitmq_utils import RabbitMQProducer
import json

# DEFINING MESSAGE
message = json.dumps({'hello': 'world'})

# SENDING
rmqp = RabbitMQProducer(
    host='localhost', port=5672, virtual_host='/', 
    username='guest', password='guest', 
    exchange='test_exc', exchange_type='topic',
    persistent_message=False
)
is_sent = rmqp.sendMessage(
    message,
    routing_key='test_key'
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
    myLogic()
    
    # ACKNOWLEDGE WORK IS DONE
    ch.basic_ack(delivery_tag=method.delivery_tag)
    return None
```

Following sample code will allow you to receive message from rabbitmq server.

```python
from rabbitmq_utils import RabbitMQConsumer

# STARTING RABBITMQ CONSUMER
rmqc = RabbitMQConsumer(
        host='localhost', port=5672, virtual_host='/', 
        username='guest', password='guest', 
        queue_name='test_que', routing_key='test_key',
    	exchange='test_exc', exchange_type='topic',
    	callback_fun=my_callback_function,
    	max_priority=2 # Use this if you want priority base queue. (Default it is None)
)
rmqc.receiveMessage()
```

## Remote Procedure Call (RPC)

RPC allow to run a function on a remote computer and wait for the result. It is a synchronous call. This package provide simplest implementation of RPC.

RPC consist of two parts. One is the **server** that will process the request and other is **client** that will generate the request to server. Following are example of RPC implementation.

### Server

```python
from rabbitmq_utils.rpc import RPCServer

# STARTING RPC SERVER
server = RPCServer(
        host='localhost', port=5672, virtual_host='/', 
        username='guest', password='guest', 
        queue_name='test_que', routing_key='test_key',
    	exchange='test_exc', exchange_type='topic',
    	callback_fun=rpc_callback_function
)
server.receiveMessage()
```

Callback function of RPC is different from consumer callback function. In this callback we will return the result back to client.

Note: **result** must be string. If it is not then use **json.dumps(**result**)** to convert it to string.

```python
def rpc_callback_function(ch, method, properties, body):
    # GETTING MESSAGE
    message = body.decode()
    
    # PERFORM YOUR LOGIC HERE
    result = myLogic()
    
    # RETURING RESPONSE
    ch.basic_publish(
        exchange='', routing_key=properties.reply_to,
        properties=pika.BasicProperties(
            correlation_id = properties.correlation_id
        ),
        body=result
    )
    
    # ACKNOWLEDGE WORK IS DONE
    ch.basic_ack(delivery_tag=method.delivery_tag)
    return None
```

### Client

```python
from rabbitmq_utils.rpc import RPCClient
import json

# DEFINING MESSAGE
message = json.dumps({'hello': 'world'})

# SENDING
client = RPCClient(
    host='localhost', port=5672, virtual_host='/', 
    username='guest', password='guest', 
    exchange='test_exc', exchange_type='topic',
    timeout=3, # wait 3 seconds for response. default is None (infinite wait).
    persistent_message=False
)
is_sent, response = client.sendMessage(
    message,
    routing_key='test_key',
    return_response=True
)

# OUTPUT
print(f'is_sent: {is_sent} \t code: {client.getCode()} \t response: {response}')
```

Client **sendMessage** receive **return_response** argument (default=False). If this is **True** then client will wait for response for desire **timeout** period.  You can receive response later if you want by using follow sample code:

```python
# SEND REQUEST
is_sent = client.sendMessage(
    message,
    routing_key
)

# PERFORM YOUR LOGIC

# RECEIVE RESPONSE
response = client.receiveResponse()
```

Always check the validity of response using status code. Following code will help you check it:

```python
status_code = client.getCode()
print(status_code)
```

Code is **integer**. Following table shows the meanings:

| Code | Meaning                            |
| ---- | ---------------------------------- |
| 200  | Response is successfully obtained. |
| 408  | Timeout occur.                     |

## Author

**Tahir Rafique**

## Releases

| Date      | Version | Summary                                         |
| --------- | ------- | ----------------------------------------------- |
| 13-Dec-23 | v1.4.0  | Adding queue priority in producer and consumer. |
| 14-Jul-23 | v1.3.0  | Adding persistent message option.               |
| 14-Jul-23 | v1.2.1  | Correcting documentation.                       |
| 21-Jun-23 | v1.2.0  | Adding RPC to module.                           |
| 27-Apr-23 | v1.0.1  | Improving default callback function.            |
| 27-Apr-23 | v1.0.0  | Initial build                                   |

