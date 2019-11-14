from flask import request, jsonify, abort
from flask import current_app as app
from .models import Client
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest, UnsupportedMediaType
import traceback
from . import Session
import bcrypt
import jwt

# Client Routes #########################################################################################################
@app.route('/client/create', methods=['POST'])
def create_client():
    session = Session()
    new_client= None
    if request.headers['Content-Type'] != 'application/json':
        abort(UnsupportedMediaType.code)
    content = request.json
    try:
        username = content['username']
        password =  bcrypt.hashpw(content['password'].encode(), bcrypt.gensalt())        
        new_client = Client(
            username,
            password
        )
        session.add(new_client)  
        session.commit()        
    except KeyError:
        session.rollback()
        session.close()
        abort(BadRequest.code)
    response = jsonify(new_client.as_dict())   
    session.close()
    return response

@app.route('/client/create_jwt', methods=['GET'])
def create_jwt():
    session = Session()
    if request.headers['Content-Type'] != 'application/json':
        abort(UnsupportedMediaType.code)
    content = request.json

    response = None

    try:
        username = content['username']
        password = content['password'].encode()       

        user = session.query(Client).filter(Client.username == username).one()

        if not bcrypt.checkpw(password, user.password):
            raise Exception

        key = 'secret'
        payload = {}
        payload['id'] = user.id
        payload['username'] = username
        payload['service'] = False
        payload['perms'] = 'ADMIN'

        response = jwt.encode(payload, key, algorithm='HS256')
        
        session.add(new_client)  
        session.commit()        
    except:
        session.rollback()
        session.close()
        abort(BadRequest.code)

    session.close()
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


