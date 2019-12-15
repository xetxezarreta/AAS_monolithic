import pika
import json

def send_message(exchange, routing_key, message):
    credentials = pika.PlainCredentials('guest', 'guest')
    parameters = pika.ConnectionParameters('192.168.17.4', 5672, '/', credentials)
    connection = pika.BlockingConnection(parameters) 
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange, exchange_type='direct')
    channel.basic_publish(exchange=exchange, routing_key=routing_key, body=json.dumps(message))
    connection.close()

def send_log(message):
    exchange = 'logger_exchange'
    routing_key = message['microservice']+'.info'
    credentials = pika.PlainCredentials('guest', 'guest')
    parameters = pika.ConnectionParameters('192.168.17.4', 5672, '/', credentials)
    connection = pika.BlockingConnection(parameters) 
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange, exchange_type='topic')
    channel.basic_publish(exchange=exchange, routing_key=routing_key, body=json.dumps(message))
    connection.close()
