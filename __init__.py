__version__='1.3.0'

try:
    from .consumer import RabbitMQConsumer
    from .producer import RabbitMQProducer
except:
    pass