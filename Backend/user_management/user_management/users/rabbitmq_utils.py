import json

import pika
from django.conf import settings


def get_rabbitmq_connection():
    credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(
        settings.RABBITMQ_HOST, settings.RABBITMQ_PORT, "/", credentials
    )
    return pika.BlockingConnection(parameters)


def publish_message(queue_name, message):
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    # Ensure the message is a JSON string
    message = json.dumps(message) if isinstance(message, dict) else message
    channel.basic_publish(
        exchange="",
        routing_key=queue_name,
        body=message,
        properties=pika.BasicProperties(delivery_mode=2),
    )
    connection.close()


def consume_message(queue_name, callback):
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    try:
        channel.start_consuming()
    except Exception as e:
        print(f"Error consuming message: {e}")
    finally:
        connection.close()
