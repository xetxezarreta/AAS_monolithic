import sys
import pika
import threading
from .models import Payment
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
    
    # Payment reserve
    @staticmethod
    def payment_reserve(ch, method, properties, body):
        print("Payment reserve callback", flush=True)
        session = Session() 
        content = json.loads(body)
        status = True
        
        try:          
            user = session.query(Payment).filter(Payment.userId == content['userId']).one()
            money = content['number_of_pieces'] * 10
            if user.money < money:
                raise NoResultFound("No tiene dinero suficiente")
            user.money -= money
            user.reserved += money
            session.commit() 
        except:
            status = False
            session.rollback()     
        content['status'] = status
        content['type'] = 'PAYMENT'
        send_message("order_exchange", "sagas_payment_queue", content)
        session.close()         

    # Payment reserve cancell
    @staticmethod
    def payment_reserve_cancell(ch, method, properties, body):
        print("Payment cancell callback", flush=True)        
        session = Session() 
        content = json.loads(body)        
        try:          
            user = session.query(Payment).filter(Payment.userId == content['userId']).one()
            money = content['number_of_pieces'] * 10            
            user.money += money
            user.reserved -= money
            session.commit() 
        except:
            session.rollback()     
        session.close()  
        