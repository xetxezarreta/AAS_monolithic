import pika
import threading
from .models import Logger
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
        channel.exchange_declare(exchange=self.exchange_name, exchange_type='topic')

        # Create queue
        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        channel.queue_bind(exchange=self.exchange_name, queue=queue_name, routing_key=self.routing_key)
        channel.basic_consume(queue=queue_name, on_message_callback=self.callback_func, auto_ack=True)
        thread = threading.Thread(target=channel.start_consuming)
        thread.start()      
    
    # Payment reserve
    @staticmethod
    def log_create(ch, method, properties, body):
        print("Log callback", flush=True)   
        session = Session() 
        content = json.loads(body)
        try:
            new_log = Logger(
                log = str(content)
            )
            session.add(new_delivery) 
            session.commit()
        except Exception as e:
            print(e, flush=True)   
            session.rollback()   
        session.close()    
        
            
