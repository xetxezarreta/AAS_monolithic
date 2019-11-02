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
    def __init__(self):  
        # Rabbit config
        exchange_name = 'order_exchange'
        credentials = pika.PlainCredentials('guest', 'guest')
        parameters = pika.ConnectionParameters('192.168.17.4', 5672, '/', credentials)
        connection = pika.BlockingConnection(parameters) 
        self.channel = connection.channel()  
        self.channel.exchange_declare(exchange=exchange_name, exchange_type='direct')
        # Queues declare
        self.__declare_queue(exchange_name, 'machine_queue', self.machine_callback)
        self.__declare_queue(exchange_name, 'payment_queue', self.payment_callback)    
        self.__declare_queue(exchange_name, 'delivery_queue', self.delivery_callback)          
        # Thread
        thread = threading.Thread(target=self.channel.start_consuming)
        thread.start()     
        #thread.join(0)
    
    def __declare_queue(self, exchange_name, routing_key, callback_func):
        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        self.channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)
        self.channel.basic_consume(queue=queue_name, on_message_callback=callback_func, auto_ack=True)
    
    # Machine callback
    def machine_callback(self, ch, method, properties, body):
        content = json.loads(body)
        
        delivery_info = {}
        delivery_info['orderId'] = content['orderId']
        delivery_info['delivered'] = True
        send_message("delivery_exchange", "update_delivery_queue", delivery_info)        

    # Payment callback
    def payment_callback(self, ch, method, properties, body):
        session = Session()
        content = json.loads(body)        
                
        if content['status']:
            print("bien")
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
            print("mal")
        session.close()

    # Delivery callback
    def delivery_callback(self, ch, method, properties, body):
        pass
