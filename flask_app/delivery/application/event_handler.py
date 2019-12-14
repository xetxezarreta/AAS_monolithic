import pika
import threading
from .models import Delivery
from sqlalchemy.orm.exc import NoResultFound
from .event_publisher import send_message
from . import Session
import json
from .log import create_log

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
                create_log(__file__, 'Delivery created')
            else:
                status = False
        except:
            status = False
            session.rollback()   
             
        content['status'] = status
        content['type'] = 'DELIVERY'
        send_message("delivery_exchange", "sagas_delivery_queue", content)
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
            create_log(__file__, 'Delivery cancelled')
        except Exception as e:
            create_log(__file__, e)
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
            delivery = session.query(Delivery).filter(Delivery.orderId == new_delivery.orderId).one()
            delivery.delivered = new_delivery.delivered               
            session.commit()
            create_log(__file__, 'Delivery updated')         
        except Exception as e:
            session.rollback()
            create_log(__file__, e)
        session.close()
