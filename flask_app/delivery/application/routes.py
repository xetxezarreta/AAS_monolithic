from flask import request, jsonify, abort
from flask import current_app as app
from .models import Delivery
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest, UnsupportedMediaType
import traceback
from . import Session
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound 

# Delivery Routes #########################################################################################################
# Crea una entrega.
# Datos esperados:
#{
#	"orderId": 1,
#	"delivered": false
#}
@app.route('/create_delivery', methods=['POST'])
def create_delivery():
    session = Session()
    new_delivery = None

    if request.headers['Content-Type'] != 'application/json':        
        abort(UnsupportedMediaType.code)

    content = request.json

    try:
        new_delivery = Delivery(
            orderId = content['orderId'],
            delivered = content['delivered']
        )

        session.add(new_delivery)   
        print(new_delivery)     
        session.commit()
    except KeyError:
        session.rollback()
        session.close()
        abort(BadRequest.code)
 
    response = jsonify(new_delivery.as_dict())
    session.close()

    return response

# Actualiza el estado de la entrega. Si no existe la entrega, no hace nada.
# Datos esperados:
#{
#	"orderId": 1,
#	"delivered": false
#}
@app.route('/update_delivery', methods=['POST'])
def update_delivery():
    session = Session()    
    if request.headers['Content-Type'] != 'application/json':
        abort(UnsupportedMediaType.code)
    content = request.json
    new_delivery = None
    try:
        new_delivery = Delivery(
            orderId = content['orderId'],
            delivered = content['delivered'],
        )
        try:
            delivery = session.query(Delivery).filter(Delivery.orderId == new_delivery.orderId).one()
            delivery.delivered = new_delivery.delivered
            print(delivery)
            session.commit()
        except NoResultFound:     
            print("no existe el pedido")       
        
    except KeyError:
        session.rollback()
        session.close()
        abort(BadRequest.code)
    response = jsonify(new_delivery.as_dict())
    session.close()
    return response


# Database clean #######################################################################################################
@app.route('/clean_delivery', methods=['GET'])
def clean_payments_database():
    session = Session()
    session.query(Delivery).delete()
    session.close()
    return " filas eliminadas de payment"

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


