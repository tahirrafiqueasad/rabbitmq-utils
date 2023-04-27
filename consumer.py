""" 
Author:		 Muhammad Tahir Rafique
Date:		 2023-04-14 15:34:40
Project:	 rabbitmq-utils
Description: Provide function to start the rabbitmq consumer.
"""


import pika
import time

def callback_test(ch, method, properties, body):
    print('==================================')
    print(f'INFO: Received Message: \n\n{body.decode()}\n')
    wait_sec = body.count(b'.')
    print(f'INFO: Wating for {wait_sec} seconds.')
    time.sleep(wait_sec)
    print('INFO: Done waiting.')
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print("INFO: Acknowledgment Done.")
    print('==================================')
    print('\n\n')
    return None


class RabbitMQConsumer():
    def __init__(self, host, port, virtual_host, username, password, exchange, queue_name, routing_key, exchange_type='topic', callback_fun=callback_test) -> None:
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
        self.channel.queue_declare(queue=self.queue_name, durable=True, exclusive=False, auto_delete=False)
        
        # DECLARE EXCHANGE
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