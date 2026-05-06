__version__='1.5.1'

try:
    from .consumer import RabbitMQConsumer
    from .producer import RabbitMQProducer
except:
    pass
