from flask import request, jsonify, abort
from flask import current_app as app
from .models import Order
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest, UnsupportedMediaType
import traceback
from . import Session
import requests
import pika
from .event_publisher import send_message
from .orchestrator import get_orchestrator
from .state import OrderState

# Order Routes #########################################################################################################
#{
#   "userId" : 1,
#   "zip": '20'
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
         
        message_info = {}
        message_info['orderId'] = new_order.id
        message_info['userId'] = content['userId']
        message_info['number_of_pieces'] = new_order.number_of_pieces 
        message_info['zip'] = content['zip'] 

        orchestrator = get_orchestrator()
        order_state = OrderState(message_info['orderId'], message_info['userId'], message_info['number_of_pieces'])
        orchestrator.order_state_list.append(order_state)
        
        #CAMBIAR?????
        send_message("payment_exchange", "payment_reserve_queue", message_info)
        send_message("delivery_exchange", "delivery_create_queue", message_info)
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

