import pika
import threading
from time import sleep

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
        self.declare_queue(exchange_name, 'payment_queue')        
        # Thread
        thread = threading.Thread(target=self.channel.start_consuming)
        thread.start()     
        thread.join(0)
    
    def declare_queue(self, exchange_name, routing_key):
        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        self.channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)
        self.channel.basic_consume(queue=queue_name, on_message_callback=self.callback, auto_ack=True)
        #self.channel.start_consuming()               
    
    # 'Payment' queue callback
    @staticmethod
    def callback(ch, method, properties, body):
        print(" [x] %r:%r" % (method.routing_key, body))








