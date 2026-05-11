__version__ = "1.5.1"

try:
    from .consumer import RabbitMQConsumer
    from .producer import RabbitMQProducer
    from .async_consumer import AsyncRabbitMQConsumer
    from .async_producer import AsyncRabbitMQProducer
except:
    pass
