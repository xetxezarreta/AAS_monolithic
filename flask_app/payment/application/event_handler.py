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
    def __init__(self):  
        # Rabbit config
        exchange_name = 'payment_exchange'
        credentials = pika.PlainCredentials('guest', 'guest')
        parameters = pika.ConnectionParameters('192.168.17.4', 5672, '/', credentials)
        connection = pika.BlockingConnection(parameters) 
        self.channel = connection.channel()  
        self.channel.exchange_declare(exchange=exchange_name, exchange_type='direct')
        # Queues declare
        self.__declare_queue(exchange_name, 'payment_queue')        
        # Thread
        thread = threading.Thread(target=self.channel.start_consuming)
        thread.start()     
    
    def __declare_queue(self, exchange_name, routing_key):
        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        self.channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)
        self.channel.basic_consume(queue=queue_name, on_message_callback=self.payment_callback, auto_ack=True)
    
    def __get_payment_response(self, status, payment):
        response = {}
        response['status'] = status
        if payment != None:
            response['userId'] = payment.userId
            response['orderId'] = payment.orderId
        return response
    
    # Payment callback
    def payment_callback(self, ch, method, properties, body):
        print("PAYMENT CALLBACK", flush=True)
        session = Session()               
        print(body, flush=True)
        content = json.loads(body)
        print(content, flush=True)
        response = None
        payment = None

        try:
            status = True
            payment = Payment(
                userId=content['userId'],
                orderId=content['orderId'],
                money=content['money'],         
            )     
            user = session.query(Payment).filter(Payment.userId == payment.userId).one()
            if user.money < payment.money:
                raise NoResultFound("No tiene dinero suficiente")
            user.money -= payment.money  
            session.commit()
            print(user)    
        except:
            status = False
            session.rollback()
        
        response = self.__get_payment_response(status, payment)              
        send_message("order_exchange", "payment_queue", response)
        session.close()
        