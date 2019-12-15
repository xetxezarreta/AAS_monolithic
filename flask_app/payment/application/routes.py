from flask import request, jsonify, abort
from flask import current_app as app
from .models import Payment
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest, UnsupportedMediaType
import traceback
from . import Session
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound 
from .auth import rsa_singleton
from .log import create_log

# Payment Routes #########################################################################################################
# Este POST deposita el dinero de un usuario.
# Si el usuario existe, se le suma esa cantidad de dinero.
# Si el usuario no existe, se genera un nuevo registro con el dinero que se quiere ingresar.
# Datos esperados en el post:
#{
#	"userId": 1,
#	"money": 100,
#   "jwt": "jwt"
#}
@app.route('/payment/deposit', methods=['POST'])
def perform_deposit():    
    session = Session()
    new_payment = None
    if request.headers['Content-Type'] != 'application/json':
        abort(UnsupportedMediaType.code)
    content = request.json
    
    try:
        if rsa_singleton.check_jwt(content['jwt']) == False:
            raise Exception  
        new_payment = Payment(
            userId=content['userId'],
            money=content['money'],   
            reserved=0,      
        )    
        try:           
            user = session.query(Payment).filter(Payment.userId == new_payment.userId).one()
            user.money += new_payment.money 
        except NoResultFound:     
            session.add(new_payment)         
        session.commit()
        create_log(__file__, 'Deposit performed by user '+str(new_payment.userId))   
    except Exception as e:
        create_log(__file__, str(e))   
        session.rollback()
        session.close()
        abort(BadRequest.code)

    response = jsonify(new_payment.as_dict())
    session.close()
    return response

# Health-check #######################################################################################################
@app.route('/payment/health', methods=['HEAD', 'GET'])
@app.route('/health', methods=['HEAD', 'GET'])
def health_check():
    print("HEALTHCHECK", flush=True)
    return "OK"

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


