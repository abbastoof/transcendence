import json
import pika
from django.conf import settings

# Singleton pattern for managing RabbitMQ connection
class RabbitMQManager:
    _connection = None

    @classmethod
    def get_connection(cls):
        if cls._connection is None or not cls._connection.is_open:
            cls._connection = cls._create_connection()
        return cls._connection

    @classmethod
    def _create_connection(cls):
        credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASS)
        parameters = pika.ConnectionParameters(
            settings.RABBITMQ_HOST, settings.RABBITMQ_PORT, "/", credentials
        )
        return pika.BlockingConnection(parameters)


def publish_message(queue_name, message):
    connection = RabbitMQManager.get_connection()
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    try:
        # Ensure the message is a JSON string
        message = json.dumps(message) if isinstance(message, dict) else message
        channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2),
        )
    except Exception as e:
        print(f"Error publishing message: {e}")
    finally:
        # Do not close the connection here; let it be managed by the RabbitMQManager
        pass


def consume_message(queue_name, callback):
    connection = RabbitMQManager.get_connection()
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    try:
        channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
        channel.start_consuming()
    except Exception as e:
        print(f"Error consuming message: {e}")
    finally:
        # Do not close the connection here; let it be managed by the RabbitMQManager
        pass
