from . import Session
import pika
import threading
from .models import Piece
from werkzeug.exceptions import BadRequest
from flask import abort
from .event_publisher import send_message
from .machine import Machine
import json
from .auth import rsa_singleton

my_machine = Machine()

class Rabbit():
    def __init__(self):  
        # Rabbit config
        exchange_name = 'machine_exchange'
        credentials = pika.PlainCredentials('guest', 'guest')
        parameters = pika.ConnectionParameters('192.168.17.4', 5672, '/', credentials)
        connection = pika.BlockingConnection(parameters) 
        self.channel = connection.channel()  
        self.channel.exchange_declare(exchange=exchange_name, exchange_type='direct')
        # Queues declare
        self.__declare_queue(exchange_name, 'machine_queue', self.machine_callback)    
        # Thread
        thread = threading.Thread(target=self.channel.start_consuming)
        thread.start()     
    
    def __declare_queue(self, exchange_name, routing_key, callback_func):
        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        self.channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)
        self.channel.basic_consume(queue=queue_name, on_message_callback=callback_func, auto_ack=True)
    
    # Machine callback
    def machine_callback(self, ch, method, properties, body):
        session = Session()        
        content = json.loads(body)

        try:
            if rsa_singleton.check_jwt(content['jwt']) == False:
                raise Exception 
            number_of_pieces = content['number_of_pieces']

            pieces_list = list()
            for _ in range(number_of_pieces):
                piece = Piece()
                piece.orderId = content['orderId']     
                piece.jwt = content['jwt']       
                session.add(piece)    
                session.commit()     
                session.refresh(piece)
                print(piece)      
                pieces_list.append(piece)

            if pieces_list: # miramos si hay elemento en la lista.
                my_machine.add_pieces_to_queue(pieces_list)               
            
        except KeyError:
            session.rollback()
            session.close()
            abort(BadRequest.code)

        session.close()
