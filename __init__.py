__version__='1.4.0'

try:
    from .consumer import RabbitMQConsumer
    from .producer import RabbitMQProducer
except:
    pass
