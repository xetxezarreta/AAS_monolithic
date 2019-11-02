from flask import request, jsonify, abort
from flask import current_app as app
from .models import Order
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest, UnsupportedMediaType
import traceback
from . import Session
import requests
import pika
from .event_publisher import send_message

# Order Routes #########################################################################################################
#{
#   "userId" : 1    
#   "number_of_pieces" : 2,
#}
@app.route('/order/create', methods=['POST'])
def create_order():
    print("POST create order", flush=True)
    session = Session()
    if request.headers['Content-Type'] != 'application/json':
        abort(UnsupportedMediaType.code)
    content = request.json

    status = True
    try:      
        new_order =  Order(
            number_of_pieces = content['number_of_pieces'],         
        )    
        session.add(new_order) 
        session.commit()

        # payment_response =  request_payment(content['userId'], new_order.number_of_pieces)      
        payment = {}
        payment['orderId'] = new_order.id
        payment['userId'] = content['userId']
        payment['money'] = 10 * new_order.number_of_pieces # 10 por pieza 
        send_message("payment_exchange", "payment_queue", payment)  
    except KeyError:
        status = False
        session.rollback()
        session.close()
        abort(BadRequest.code)

    session.close()
    return get_order_response(status)

# Respuesta del POST del order.
# EJEMPLO:
#{
#    "status": true
#}
def get_order_response(status):
    response = {}
    response['status'] = status
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


