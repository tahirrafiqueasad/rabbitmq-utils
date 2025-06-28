""" 
Author:		 Muhammad Tahir Rafique
Date:		 2023-06-19 16:26:01
Project:	 Rabbitmq Utils
Description: Provide class to make RPC Client.
"""

import uuid

from rabbitmq_utils import RabbitMQProducer


class RPCClient(RabbitMQProducer):
    """RPC Client Class."""
    def __init__(self, host, port, virtual_host, username, password, exchange, exchange_type='topic', timeout=None, persistent_message=False) -> None:
        super().__init__(host, port, virtual_host, username, password, exchange, exchange_type, persistent_message)
        
        self.timeout = timeout
        
        self.channel = self.getChannel()
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

        # STATE VARIABLES
        self.response = None
        self.corr_id = None
        self._code = None
        return None
    
    def getCode(self):
        """Return the code."""
        return self._code
    
    def setCode(self, code):
        """Set the code."""
        self._code = code
        return None
    
    def getResponse(self):
        """Returning response."""
        return self.response
    
    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body.decode()
        return None
    
    def closeConnection(self):
        """Close the channel connection."""
        self.connection.close()
        return None
    
    def receiveResponse(self):
        """Receiving response."""
        # GETTING RESPONSE
        self.connection.process_data_events(time_limit=self.timeout)
        
        response = self.getResponse()
        if not response:
            self.setCode(408) # Timeout error occur.
        else:
            self.setCode(200)
            
        # UPDATING RESPONSE
        self.response = response
        return response
    
    def sendMessage(self, message, routing_key, return_response=False):
        """Send the message to rabbitmq."""
        # SENDING RESPONSE
        self.response = None
        self.corr_id = str(uuid.uuid4())
        kwargs = {
            'reply_to': self.callback_queue,
            'correlation_id': self.corr_id
        }
        
        is_sent = super().sendMessage(message, routing_key, close_connection=False, **kwargs)
        
        # RECEIVING RESPONSE
        if return_response:
            response = self.receiveResponse()
        
        # CLOSING CONNECTION
        self.closeConnection()
        
        # RETURNING RESPONSE
        if return_response:
            return is_sent, response
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
    client = RPCClient(host, port, virtual_host, username, password, exchange, timeout=3)
    is_sent, response = client.sendMessage(
        message,
        routing_key,
        return_response=True
    )
    
    # OUTPUT
    print(f'is_sent: {is_sent} \t code: {client.getCode()} \t response: {response}')
