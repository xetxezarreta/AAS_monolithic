from flask import request, jsonify, abort
from flask import current_app as app
from .models import Delivery
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest, UnsupportedMediaType
import traceback
from . import Session
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound 
from .log import create_log

# Delivery Routes #########################################################################################################
@app.route('/delivery/deliveries', methods=['GET'])
def view_deliveries():
    session = Session()
    deliveries = session.query(Delivery).all()
    response = jsonify(Delivery.list_as_dict(deliveries))
    session.close()
    create_log(__file__, 'View deliveries requested')
    return response

# Health-check #######################################################################################################
@app.route('/delivery/health', methods=['HEAD', 'GET'])
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


