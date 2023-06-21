""" 
Author:		 Muhammad Tahir Rafique
Date:		 2023-06-20 12:20:13
Project:	 Rabbitmq Utils
Description: Provide RPC Server class.
"""
import time
import pika

from rabbitmq_utils import RabbitMQConsumer


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
    
    # RETURING RESPONSE
    response = wait_sec
    ch.basic_publish(exchange='',
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(correlation_id = \
                                            properties.correlation_id),
        body=str(response)
        )
    
    # ACKNOWLEDGE WORK IS DONE
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print("INFO: Acknowledgment Done.")
    print('==================================')
    print('\n\n')
    return None

class RPCServer(RabbitMQConsumer):
    def __init__(self, host, port, virtual_host, username, password, queue_name, routing_key, exchange='', exchange_type='topic', callback_fun=callback_test) -> None:
        super().__init__(host, port, virtual_host, username, password, queue_name, routing_key, exchange, exchange_type, callback_fun)
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
    server = RPCServer(host, port, virtual_host, username, password, queue_name, routing_key, exchange)
    server.receiveMessage()