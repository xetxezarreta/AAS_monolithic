from flask import request, jsonify, abort
from flask import current_app as app
from .models import Logger
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest, UnsupportedMediaType
import traceback
from . import Session

# Logger Routes #########################################################################################################
@app.route('/logger/logs', methods=['GET'])
def view_deliveries():
    session = Session()
    logs = session.query(Logger).all()
    response = jsonify(Logger.list_as_dict(logs))
    session.close()
    return response

# Health-check #######################################################################################################
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


