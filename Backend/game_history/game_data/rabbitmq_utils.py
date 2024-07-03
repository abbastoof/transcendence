import pika # RabbitMQ library
import json
from django.conf import settings

class RabbitMQManager:
    _connection = None # Connection to RabbitMQ server is none by default so that we can check if it is connected or not

    @classmethod # Class method to connect to RabbitMQ server
    def get_connection(cls):
        if not cls._connection or cls._connection.is_closed: # If connection is not established or connection is closed
            cls._connection = cls.create_connection()
        return cls._connection # Return the connection to RabbitMQ server

    @classmethod # Class method to create connection to RabbitMQ server
    def create_connection(cls):
        credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASS) # Create credentials to connect to RabbitMQ server
        parameters = pika.ConnectionParameters(settings.RABBITMQ_HOST, settings.RABBITMQ_PORT, "/", credentials=credentials) # Create connection parameters to RabbitMQ server
        return pika.BlockingConnection(parameters) # Create a blocking connection to RabbitMQ server because we want to wait for the connection to be established before proceeding

    @staticmethod # Static method to publish message to RabbitMQ server
    def publish_message(queue_name, message):
        connection = RabbitMQManager.get_connection()
        channel = connection.channel() # Create a channel to RabbitMQ server to publish message
        channel.queue_declare(queue=queue_name, durable=True) # Declare a queue to RabbitMQ server with the given name and make it durable so that it persists even if RabbitMQ server restarts
        channel.basic_publish(
            exchange='', # Publish message to default exchange
            routing_key=queue_name, # Publish message to the given queue
            body=json.dumps(message), # Convert message to JSON format before publishing
            properties=pika.BasicProperties(delivery_mode=2) # Make the message persistent so that it is not lost even if RabbitMQ server restarts
        )
        connection.close()

    @staticmethod # Static method to consume message from RabbitMQ server
    def consume_message(queue_name, callback): # Callback function to be called when a message is received
        connection = RabbitMQManager.get_connection()
        channel = connection.channel() # Create a channel to RabbitMQ server to consume message
        channel.queue_declare(queue=queue_name, durable=True) # Declare a queue to RabbitMQ server with the given name and make it durable so that it persists even if RabbitMQ server restarts

        def wrapper(ch, method, properties, body): # Wrapper function to call the callback function with the received message
            callback(json.loads(body)) # Convert the received message from JSON format before calling the callback function
            ch.basic_ack(delivery_tag=method.delivery_tag) # Acknowledge the message so that it is removed from the queue

        channel.basic_consume(queue=queue_name, on_message_callback=wrapper) # Consume message from the given queue and call the wrapper function when a message is received
        channel.start_consuming() # Start consuming messages from RabbitMQ server
