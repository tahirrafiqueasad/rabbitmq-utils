__version__ = "1.6.0"

try:
    from .async_consumer import AsyncRabbitMQConsumer
    from .async_producer import AsyncRabbitMQProducer
    from .consumer import RabbitMQConsumer
    from .producer import RabbitMQProducer
except:
    pass
