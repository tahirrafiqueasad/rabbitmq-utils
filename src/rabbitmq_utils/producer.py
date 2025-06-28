""" 
Author:		 Muhammad Tahir Rafique
Date:		 2023-04-13 19:54:14
Project:	 rabbitmq-utils
Description: Provide function to send the message to rabbitmq exchange.
"""

import pika

class RabbitMQProducer():
    def __init__(self, host, port, virtual_host, username, password, exchange='', exchange_type='topic', persistent_message=False) -> None:
        """Constructor."""
        self.host = host
        self.port = port
        self.virtual_host = virtual_host
        self.username = username
        self.password = password
        self.exchange = exchange
        self.exchange_type = exchange_type
        
        # STATE VARIABLES
        self.channel = None
        self.connection = None
        self._isSent = None
        
        # DELIVERTY MODE
        if persistent_message:
            self._delivery_mode = pika.DeliveryMode.Persistent
        else:
            self._delivery_mode = pika.DeliveryMode.Transient
        return None
    
    def isSent(self):
        """Getting send status."""
        return self._isSent
    
    def setSentStatus(self, status):
        """Setting send status."""
        self._isSent = status
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
            
            # DECLARE EXCHANGE
            if self.exchange != '':
                self.channel.exchange_declare(exchange=self.exchange, exchange_type=self.exchange_type, durable=True)
            
            # Turn on delivery confirmations
            self.channel.confirm_delivery()
        return self.channel
    
    def closeConnection(self):
        """Close the channel connection."""
        self.connection.close()
        return None
    
    def sendMessage(self, message, routing_key, close_connection=True, **kwargs):
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
                    delivery_mode=self._delivery_mode,
                    **kwargs
                )
            )
            is_sent = True
        except pika.exceptions.UnroutableError:
            is_sent = False
            
        # UDATING STATUS
        self.setSentStatus(is_sent)
        
        # CLOSING CONNECTION
        if close_connection:
            self.closeConnection()
        return is_sent


if __name__ == "__main__":
    # INFORMATION
    host = 'localhost'
    port = 9020
    virtual_host = '/'
    username = 'guest'
    password = 'guest'
    exchange = 'test_exc'
    routing_key = 'test_key'
    
    # DEFINING MESSAGE
    import json
    message = json.dumps({'wait_time': 2})
    
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