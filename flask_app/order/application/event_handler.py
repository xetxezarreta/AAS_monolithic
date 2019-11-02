import pika
import threading
from .models import Order
from werkzeug.exceptions import BadRequest
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound 
from flask import abort
from .event_publisher import send_message
from . import Session
import json

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
        send_message("delivery_exchange", "update_delivery_queue", delivery_info)

    # Payment callback
    @staticmethod
    def payment_callback(ch, method, properties, body):
        print("ORDER-payment callback", flush=True)
        session = Session()
        content = json.loads(body)        
                    
        if content['status']:
            print("bien", flush=True)
            order = session.query(Order).filter(Order.id == content['orderId']).one()
            # Mandar piezas al machine
            manufacture_info = {}
            manufacture_info['orderId'] = order['id'] 
            manufacture_info['number_of_pieces'] = order['number_of_pieces'] 
            send_message("machine_exchange", "machine_queue", manufacture_info)                
            # Crear el delivery
            delivery_info = {}
            delivery_info['orderId'] = order['id']
            delivery_info['delivered'] = False
            send_message("delivery_exchange", "create_delivery_queue", delivery_info)
        else:
            print("mal", flush=True)
        session.close()

    # Delivery callback
    @staticmethod
    def delivery_callback(ch, method, properties, body):
        pass
