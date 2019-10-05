from flask import request, jsonify, abort
from flask import current_app as app
from .models import Payment
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest, UnsupportedMediaType
import traceback
from . import Session
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound 

# Payment Routes #########################################################################################################

# Este POST deposita el dinero de un usuario.
# Si el usuario existe, se le suma esa cantidad de dinero.
# Si el usuario no existe, se genera un nuevo registro con el dinero que se quiere ingresar.
# Datos esperados en el post:
#{
#	"userId": 1,
#	"money": 100
#}
@app.route('/deposit', methods=['POST'])
def perform_deposit():    
    session = Session()
    new_payment = None
    if request.headers['Content-Type'] != 'application/json':
        abort(UnsupportedMediaType.code)
    content = request.json
    
    try:
        new_payment = Payment(
            userId=content['userId'],
            money=content['money'],         
        )             
        try:           
            user = session.query(Payment).filter(Payment.userId == new_payment.userId).one()
            user.money += new_payment.money 
            print(user)
        except NoResultFound:     
            session.add(new_payment)    

        session.commit()
    except KeyError:
        session.rollback()
        session.close()
        abort(BadRequest.code)

    response = jsonify(new_payment.as_dict())
    session.close()
    return response

# Este POST cobra un pago a un usuario.
# Si el usuario existe, se le resta esa cantidad de dinero.
# Si el usuario no existe o no tiene suficiente dinero, no se puede proceder al pago.
# Datos esperados en el post:
#{
#	"userId": 1,
#	"money": 100  #Dinero a cobrar siempre en positivo para luego restar!!
#}
@app.route('/payment', methods=['POST'])
def request_payment():    
    session = Session()

    if request.headers['Content-Type'] != 'application/json':
        abort(UnsupportedMediaType.code)
    content = request.json

    status = True

    try:
        payment = Payment(
            userId=content['userId'],
            money=content['money'],         
        )     
        try:           
            user = session.query(Payment).filter(Payment.userId == payment.userId).one()
            if user.money < payment.money:
                raise NoResultFound("No tiene dinero suficiente")
            user.money -= payment.money  
            session.commit()
            print(user)
        except NoResultFound:     
            print("no tiene dinero") 
            status = False       
        finally:
            response = get_payment_response(user.userId, status)
        
    except KeyError:
        session.rollback()
        session.close()
        abort(BadRequest.code)    

    session.close()
    return response

# Respuesta del POST del payment.
# Si se puede realizar el pago, status=True
# Si no se puede realizar el pago, status=False
def get_payment_response(userId, status):
    response = {}
    response['userId'] = userId
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


