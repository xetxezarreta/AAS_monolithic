import pika
import threading
from .models import Delivery
from werkzeug.exceptions import BadRequest
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound 
from flask import abort
from .event_publisher import send_message
from . import Session
import json

class Rabbit():
    def __init__(self):  
        # Rabbit config
        exchange_name = 'delivery_exchange'
        credentials = pika.PlainCredentials('guest', 'guest')
        parameters = pika.ConnectionParameters('192.168.17.4', 5672, '/', credentials)
        connection = pika.BlockingConnection(parameters) 
        self.channel = connection.channel()  
        self.channel.exchange_declare(exchange=exchange_name, exchange_type='direct')
        # Queues declare
        self.__declare_queue(exchange_name, 'create_delivery_queue', self.create_delivery_callback)     
        self.__declare_queue(exchange_name, 'update_delivery_queue', self.update_delivery_callback)   
        # Thread
        thread = threading.Thread(target=self.channel.start_consuming)
        thread.start()     
    
    def __declare_queue(self, exchange_name, routing_key, callback_func):
        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        self.channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)
        self.channel.basic_consume(queue=queue_name, on_message_callback=callback_func, auto_ack=True) 
    
    # Create delivery callback
    def create_delivery_callback(self, ch, method, properties, body):
        print("DELIVERY CREATE CALLBACK", flush=True)
        session = Session()
        new_delivery = None
        content = json.loads(body)
        print(content, flush=True)

        try:
            new_delivery = Delivery(
                orderId = content['orderId'],
                delivered = content['delivered'],
            )
            session.add(new_delivery)   
            session.commit()
        except KeyError:
            session.rollback()
        session.close()

    # Update delivery callback
    def update_delivery_callback(self, ch, method, properties, body):
        print("DELIVERY UPDATE CALLBACK", flush=True)
        session = Session()            
        content = json.loads(body)

        try:
            new_delivery = Delivery(
                orderId = content['orderId'],
                delivered = content['delivered'],
            )
            try:
                delivery = session.query(Delivery).filter(Delivery.orderId == new_delivery.orderId).one()
                delivery.delivered = new_delivery.delivered
                print(delivery)
                session.commit()
            except NoResultFound:     
                print("no existe el pedido")                  
        except KeyError:
            session.rollback()

        session.close()
        