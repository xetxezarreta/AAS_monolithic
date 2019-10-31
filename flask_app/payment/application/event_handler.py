import pika
from threading import Thread

class Rabbit(Thread):
    def __init__(self):  
        Thread.__init__(self)
        # Rabbit config
        exchange_name = 'payment_exchange'
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.17.4:5672'))    
        self.channel = connection.channel()  
        self.channel.exchange_declare(exchange=exchange_name, exchange_type='direct')
        # Queues declare
        self.declare_queue(exchange_name, 'payment_queue')        
        self.start()
    
    def declare_queue(self, exchange_name, routing_key):
        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        self.channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)
        self.channel.basic_consume(queue=queue_name, on_message_callback=self.callback, auto_ack=True)
        self.channel.start_consuming()
    
    def run(self):
        while True:
            pass
    
    # 'Payment' queue callback
    @staticmethod
    def callback(ch, method, properties, body):
        print(" [x] %r:%r" % (method.routing_key, body))








