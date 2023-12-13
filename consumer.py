""" 
Author:		 Muhammad Tahir Rafique
Date:		 2023-04-14 15:34:40
Project:	 rabbitmq-utils
Description: Provide function to start the rabbitmq consumer.
"""


import pika
import time

def callback_test(ch, method, properties, body):
    # GETTING MESSAGE
    message = body.decode()
    print('==================================')
    print(f'INFO: Received Message: \n\n{message}\n')
    
    # PERFORM YOUR LOGIC HERE
    import json
    wait_sec = json.loads(message)['wait_time']
    print(f'INFO: Wating for {wait_sec} seconds.')
    time.sleep(wait_sec)
    print('INFO: Done waiting.')
    
    
    # ACKNOWLEDGE WORK IS DONE
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print("INFO: Acknowledgment Done.")
    print('==================================')
    print('\n\n')
    return None


class RabbitMQConsumer():
    def __init__(self, host, port, virtual_host, username, password, queue_name, routing_key, exchange='', exchange_type='topic', callback_fun=callback_test, max_priority=None) -> None:
        """Constructor."""
        self.host = host
        self.port = port
        self.virtual_host = virtual_host
        self.username = username
        self.password = password
        self.exchange = exchange
        self.queue_name = queue_name
        self.routing_key = routing_key
        self.exchange_type = exchange_type
        self.callback_fun = callback_fun
        self.max_priority = max_priority # Message priority.
        
        # STATE VARIABLES
        self.channel = None
        return None
    
    def makeConnection(self):
        """Making connection with rabbitmq."""
        credentials = pika.credentials.PlainCredentials(self.username, self.password)
        connection_params = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            virtual_host=self.virtual_host, 
            credentials=credentials
            )
        connection = pika.BlockingConnection(connection_params)
        self.channel = connection.channel()
        
        # DECLARE QUEUE
        if self.max_priority:
            self.channel.queue_declare(queue=self.queue_name, durable=True, exclusive=False, auto_delete=False, arguments={"x-max-priority": self.max_priority})
        else:
            self.channel.queue_declare(queue=self.queue_name, durable=True, exclusive=False, auto_delete=False)
        
        # DECLARE EXCHANGE
        if self.exchange != '': # No delecration and binding is required for default exchange.
            self.channel.exchange_declare(exchange=self.exchange, exchange_type=self.exchange_type, durable=True)
        
            # BINDING QUEUE
            self.channel.queue_bind(exchange=self.exchange, queue=self.queue_name, routing_key=self.routing_key)
        return None
    
    def startReveiving(self):
        """Start the consumer consuming process."""
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.callback_fun)
        self.channel.start_consuming()
        return None
    
    def receiveMessage(self):
        """Main function of the application."""
        # MAKING CONNECTION
        self.makeConnection()
        
        # STARTING CINSUMPTION
        self.startReveiving()
        return None

if __name__ == "__main__":
    # INFORMATION
    host = 'localhost'
    port = 9020
    virtual_host = '/'
    username = 'guest'
    password = 'guest'
    exchange = 'test_exc'
    routing_key = 'test_key'
    queue_name = 'test_que'
    
    # RECEIVING
    consumer = RabbitMQConsumer(host, port, virtual_host, username, password, queue_name, routing_key, exchange)
    consumer.receiveMessage()