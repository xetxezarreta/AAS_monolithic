import pika
import threading
from .models import Order
from .event_publisher import send_message
import json
from .orchestrator import get_orchestrator

class Rabbit():
    def __init__(self, exchange_name, routing_key, callback_func):        
        self.exchange_name = exchange_name
        self.routing_key = routing_key
        self.callback_func = callback_func
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
        channel.basic_consume(queue=queue_name, on_message_callback=self.callback_func, auto_ack=True)
        thread = threading.Thread(target=channel.start_consuming)
        thread.start()      
    
    # Machine callback
    @staticmethod
    def machine_callback(ch, method, properties, body):
        print("ORDER-machine callback", flush=True)
        content = json.loads(body)
            
        delivery_info = {}
        delivery_info['orderId'] = content['orderId']
        delivery_info['delivered'] = True
        send_message("delivery_exchange", "delivery_update_queue", delivery_info)    

    # Sagas callback for Payment
    @staticmethod
    def sagas_payment_callback(ch, method, properties, body):
        print("sagas-clabbackkkkkk", flush=True)
        content = json.loads(body)
        orchestrator = get_orchestrator()
        orchestrator.treat_message(content)

    # Sagas callback for Delivery
    @staticmethod
    def sagas_delivery_callback(ch, method, properties, body):
        content = json.loads(body)
        orchestrator = get_orchestrator()
        orchestrator.treat_message(content)

    
