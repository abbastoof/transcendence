import json
import aio_pika
import asyncio
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class RabbitMQManager:
    _connection = None

    @classmethod
    async def get_connection(cls):
        if cls._connection is None or cls._connection.is_closed:
            cls._connection = await cls._create_connection()
        return cls._connection

    @classmethod
    async def _create_connection(cls):
        try:
            connection = await aio_pika.connect_robust(
                host=settings.RABBITMQ_HOST,
                port=int(settings.RABBITMQ_PORT),
                virtualhost="/",
                login=settings.RABBITMQ_USER,
                password=settings.RABBITMQ_PASS,
                heartbeat=600  # 600 seconds or adjust according to your needs
            )
            return connection
        except Exception as e:
            logger.error(f"Error creating RabbitMQ connection: {e}")
            raise

async def publish_message(queue_name, message):
    try:
        connection = await RabbitMQManager.get_connection()
        async with connection.channel() as channel:
            queue = await channel.declare_queue(queue_name, durable=True)
            # Ensure the message is a JSON string
            message = json.dumps(message) if isinstance(message, dict) else message
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=message.encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key=queue_name,
            )
            logger.info(f"Message published to queue {queue_name}: {message}")
    except aio_pika.exceptions.AMQPConnectionError as e:
        logger.error(f"RabbitMQ connection error: {e}")
        # Try to reconnect
        RabbitMQManager._connection = None
        await publish_message(queue_name, message)
    except Exception as e:
        logger.error(f"Error publishing message: {e}")

async def consume_message(queue_name, callback):
    try:
        connection = await RabbitMQManager.get_connection()
        async with connection.channel() as channel:
            queue = await channel.declare_queue(queue_name, durable=True)
            async for message in queue:
                async with message.process():
                    await callback(message)
                    logger.info(f"Message consumed from queue {queue_name}: {message.body.decode()}")
                    break
    except aio_pika.exceptions.AMQPConnectionError as e:
        logger.error(f"RabbitMQ connection error: {e}")
        # Attempt to reconnect and restart consuming
        RabbitMQManager._connection = None
        await consume_message(queue_name, callback)
    except Exception as e:
        logger.error(f"Error consuming message: {e}")
