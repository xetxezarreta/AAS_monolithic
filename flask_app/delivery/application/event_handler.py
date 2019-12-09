<<<<<<< HEAD
import pika
import threading
from .models import Delivery
from sqlalchemy.orm.exc import NoResultFound
from .event_publisher import send_message
from . import Session
import json
from .myjwt import rsa_singleton

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
    def delivery_create(ch, method, properties, body):
        print("Delivery create callback", flush=True)   
        session = Session() 
        content = json.loads(body)
        status = True
        
        try:  
            if rsa_singleton.check_jwt(content['jwt']) == False:
                raise Exception
            new_delivery = Delivery(
                orderId = content['orderId'],
                delivered = False,
            )
            if content['zip'] == '01' or content['zip'] == '20' or content['zip'] == '48':
                session.add(new_delivery) 
                session.commit()
            else:
                status = False
        except:
            status = False
            session.rollback()   
             
        content['status'] = status
        content['type'] = 'DELIVERY'
        send_message("order_exchange", "sagas_queue", content)
        session.close()         

    # Payment reserve cancell
    @staticmethod
    def delivery_cancell(ch, method, properties, body):
        print("Delivery cancell callback", flush=True)        
        session = Session() 
        content = json.loads(body)        
        try:          
            if rsa_singleton.check_jwt(content['jwt']) == False:
                raise Exception
            session.query(Delivery).filter(Delivery.orderId == content['orderId']).one().delete()
            session.commit() 
        except:
            session.rollback()     
        session.close()  

    @staticmethod
    def delivery_update(ch, method, properties, body):
        print("Delivery update callback", flush=True)        
        session = Session()            
        content = json.loads(body)

        try:
            if rsa_singleton.check_jwt(content['jwt']) == False:
                raise Exception
            
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
=======
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
    def delivery_create(ch, method, properties, body):
        print("Delivery create callback", flush=True)   
        session = Session() 
        content = json.loads(body)
        status = True
        
        try:  
            new_delivery = Delivery(
                orderId = content['orderId'],
                delivered = False,
            )

            if content['zip'] == '01' or content['zip'] == '20' or content['zip'] == '48':
                session.add(new_delivery) 
                session.commit()
            else:
                status = False
        except:
            status = False
            session.rollback()   
             
        content['status'] = status
        content['type'] = 'DELIVERY'
        send_message("order_exchange", "sagas_queue", content)
        session.close()         

    # Payment reserve cancell
    @staticmethod
    def delivery_cancell(ch, method, properties, body):
        print("Delivery cancell callback", flush=True)        
        session = Session() 
        content = json.loads(body)        
        try:          
            session.query(Delivery).filter(Delivery.orderId == content['orderId']).one().delete()
            session.commit() 
        except:
            session.rollback()     
        session.close()  

    @staticmethod
    def delivery_update(ch, method, properties, body):
        print("Delivery update callback", flush=True)        
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
>>>>>>> f7c5b0da40c8339f5130b3a81aa2cb5e619a6882
