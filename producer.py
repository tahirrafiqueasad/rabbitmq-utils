""" 
Author:		 Muhammad Tahir Rafique
Date:		 2023-04-13 19:54:14
Project:	 rabbitmq-utils
Description: Provide function to send the message to rabbitmq exchange.
"""

import pika

class RabbitMQProducer():
    def __init__(self, host, port, virtual_host, username, password, exchange) -> None:
        """Constructor."""
        self.host = host
        self.port = port
        self.virtual_host = virtual_host
        self.username = username
        self.password = password
        self.exchange = exchange
        
        # STATE VARIABLES
        self.channel = None
        self.connection = None
        return None
    
    def getChannel(self):
        """Getting channel that have connection."""
        if self.channel is None:
            credentials = pika.credentials.PlainCredentials(self.username, self.password)
            connection_params = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                virtual_host=self.virtual_host, 
                credentials=credentials
                )
            self.connection = pika.BlockingConnection(connection_params)
            self.channel = self.connection.channel()
            
            # Turn on delivery confirmations
            self.channel.confirm_delivery()
        return self.channel
    
    def closeConnection(self):
        """Close the channel connection."""
        self.connection.close()
        return None
    
    def sendMessage(self, message, routing_key):
        """Send the message to rabbitmq."""
        # GETTING CHANNEL
        channel = self.getChannel()
        
        # SENDING MESSAGE
        is_sent = False
        try:
            channel.basic_publish(
                exchange=self.exchange,
                routing_key=routing_key,
                body=message,
                mandatory=True,
                properties=pika.BasicProperties(
                    content_type='text/plain',
                    delivery_mode=pika.DeliveryMode.Transient
                )
            )
            is_sent = True
        except pika.exceptions.UnroutableError:
            is_sent = False
        
        # CLOSING CONNECTION
        self.closeConnection()
        return is_sent


if __name__ == "__main__":
    # INFORMATION
    host = 'localhost'
    port = 5672
    virtual_host = '/'
    username = 'guest'
    password = 'guest'
    exchange = ''
    routing_key = 'test'
    
    # DEFINING MESSAGE
    import json
    message = json.dumps({'hello': 'world'})
    
    # SENDING
    producer = RabbitMQProducer(host, port, virtual_host, username, password, exchange)
    is_sent = producer.sendMessage(
        message,
        routing_key
    )
    
    # RESULT
    if is_sent:
        print('INFO: Message sent.')
    else:
        print('ERROR: Unable to send on desire routing key.')