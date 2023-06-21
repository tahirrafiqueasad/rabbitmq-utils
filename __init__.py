__version__='1.2.0'

try:
    from .consumer import RabbitMQConsumer
    from .producer import RabbitMQProducer
except:
    pass