from . import Session
import pika
import threading
from .models import Piece
from werkzeug.exceptions import BadRequest
from flask import abort
from .event_publisher import send_message
from .machine import Machine
import json
from .log import create_log

my_machine = Machine()

class Rabbit():
    def __init__(self, exchange_name, routing_key, callback_func):        
        self.exchange_name = exchange_name
        self.routing_key = routing_key
        self.callback_func = callback_func
        self.init_handler()

    def init_handler(self):
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
        session = Session()        
        content = json.loads(body)
        try:
            number_of_pieces = content['number_of_pieces']
            pieces_list = list()
            for _ in range(number_of_pieces):
                piece = Piece()
                piece.orderId = content['orderId']       
                session.add(piece)    
                session.commit()     
                session.refresh(piece)      
                pieces_list.append(piece)                 
            if pieces_list: # miramos si hay elemento en la lista.
                create_log(__file__, str(len(pieces_list)) + ' pieces added to machine')
                my_machine.add_pieces_to_queue(pieces_list)    
        except Exception as e:
            print(e, flush=True)
            create_log(__file__, str(e))
            session.rollback()
            session.close()
            abort(BadRequest.code)

        session.close()
