from flask import request, jsonify, abort
from flask import current_app as app
from .models import Order
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest, UnsupportedMediaType
import traceback
from . import Session
import requests
from .calls import request_payment, request_pieces_manufacture, request_create_delivery, request_update_delivery

import pika
@app.route('/rabbit-test', methods=['GET'])
def rabbit_test():
    credentials = pika.PlainCredentials('guest', 'guest')
    parameters = pika.ConnectionParameters('192.168.17.4', 5672, '/', credentials)
    connection = pika.BlockingConnection(parameters) 

    channel = connection.channel()

    channel.exchange_declare(exchange='payment_exchange', exchange_type='direct')
    message = 'hola alvaro'
    channel.basic_publish(exchange='direct_logs', routing_key='payment_queue', body=message)
    connection.close()
    return "OK"

# Order Routes #########################################################################################################
#{
#   "userId" : 1    
#   "number_of_pieces" : 2,
#}
@app.route('/order/create', methods=['POST'])
def create_order():
    session = Session()
    if request.headers['Content-Type'] != 'application/json':
        abort(UnsupportedMediaType.code)
    content = request.json

    response = None
    try:      
        new_order =  Order(
            number_of_pieces = content['number_of_pieces'],         
        )    
        session.add(new_order) 
        session.commit()

        payment_response =  request_payment(content['userId'], new_order.number_of_pieces)        

        if payment_response['status']:
            print("bien")
            # Mandar piezas al machine
            response = request_pieces_manufacture(new_order.id, new_order.number_of_pieces)
            # Crear el delivery
            request_create_delivery(new_order.id)
        else:
            print("mal") 
            response = payment_response   
  
    except KeyError:
        session.rollback()
        session.close()
        abort(BadRequest.code)

    session.close()
    return response

# Machine notifica para actualizar delivery.
#{
#    "orderId": 1
#}
@app.route('/order/notify', methods=['POST'])
def notify_piece():
    if request.headers['Content-Type'] != 'application/json':
        abort(UnsupportedMediaType.code)
    content = request.json

    response = request_update_delivery(content['orderId'])   
    print(response)  

    return response

# Error Handling #######################################################################################################
@app.errorhandler(UnsupportedMediaType)
def unsupported_media_type_handler(e):
    return get_jsonified_error(e)


@app.errorhandler(BadRequest)
def bad_request_handler(e):
    return get_jsonified_error(e)


@app.errorhandler(NotFound)
def resource_not_found_handler(e):
    return get_jsonified_error(e)


@app.errorhandler(InternalServerError)
def server_error_handler(e):
    return get_jsonified_error(e)


def get_jsonified_error(e):
    traceback.print_tb(e.__traceback__)
    return jsonify({"error_code":e.code, "error_message": e.description}), e.code


