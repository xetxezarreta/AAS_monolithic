import pika
import json

def send_message(exchange, routing_key, message):    
    try:
        print('SEND MESSAGE', flush=True)
        credentials = pika.PlainCredentials('guest', 'guest')
        parameters = pika.ConnectionParameters('192.168.17.4', 5672, '/', credentials)
        connection = pika.BlockingConnection(parameters) 
        channel = connection.channel()

        channel.exchange_declare(exchange=exchange, exchange_type='direct')
        channel.basic_publish(exchange=exchange, routing_key=routing_key, body=json.dumps(message))
        connection.close()
    except Exception as e:
        print(e, flush=True)
    

def send_log(message):
    exchange = 'logger_exchange'
    routing_key = 'logger_queue.info'
    credentials = pika.PlainCredentials('guest', 'guest')
    parameters = pika.ConnectionParameters('192.168.17.4', 5672, '/', credentials)
    connection = pika.BlockingConnection(parameters) 
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange, exchange_type='topic')
    channel.basic_publish(exchange=exchange, routing_key=routing_key, body=json.dumps(message))
    connection.close()