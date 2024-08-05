import json
import pika
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class RabbitMQManager:
    _connection = None

    @classmethod
    def get_connection(cls):
        if cls._connection is None or not cls._connection.is_open:
            cls._connection = cls._create_connection()
        return cls._connection

    @classmethod
    def _create_connection(cls):
        try:
            credentials = pika.PlainCredentials(
                settings.RABBITMQ_USER or 'guest',
                settings.RABBITMQ_PASS or 'guest'
            )
            parameters = pika.ConnectionParameters(
                host=settings.RABBITMQ_HOST or 'localhost',
                port=int(settings.RABBITMQ_PORT or 5672),
                virtual_host="/",
                credentials=credentials
            )
            return pika.BlockingConnection(parameters)
        except Exception as e:
            logger.error(f"Error creating RabbitMQ connection: {e}")
            raise

def publish_message(queue_name, message):
    try:
        connection = RabbitMQManager.get_connection()
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)
        # Ensure the message is a JSON string
        message = json.dumps(message) if isinstance(message, dict) else message
        channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2),
        ) # Make the message persistent
        logger.info(f"Message published to queue {queue_name}: {message}")
    except Exception as e:
        logger.error(f"Error publishing message: {e}")
    finally:
        # Do not close the connection here; let it be managed by the RabbitMQManager
        pass

def consume_message(queue_name, callback):
    try:
        connection = RabbitMQManager.get_connection()
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)
        channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True) # Auto acknowledge the message
        logger.info(f"Started consuming messages from queue {queue_name}")
        channel.start_consuming() # Start consuming the messages
    except Exception as e:
        logger.error(f"Error consuming message: {e}")
    finally:
        # Do not close the connection here; let it be managed by the RabbitMQManager
        pass
