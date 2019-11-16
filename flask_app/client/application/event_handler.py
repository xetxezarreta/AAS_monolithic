import pika
from .event_publisher import send_message
from .mycrypto import rsa_singleton

class Rabbit():
    def __init__(self, exchange_name, routing_key):        
        self.exchange_name = exchange_name
        self.routing_key = routing_key
        self.init_handler()

    def init_handler(self):
        print(self.routing_key, flush=True)
        # RabbitConfig
        credentials = pika.PlainCredentials('guest', 'guest')
        parameters = pika.ConnectionParameters('192.168.17.4', 5672, '/', credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()  
        channel.exchange_declare(exchange=self.exchange_name, exchange_type='direct')

        # Create queue
        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        channel.queue_bind(exchange=self.exchange_name, queue=queue_name, routing_key=self.routing_key)

        # Send public key
        content = {}
        content['public_key'] = rsa_singleton.get_public_key()
        send_message(self.exchange_name, self.routing_key, content)
        