from flask import request, jsonify, abort
from flask import current_app as app
from .models import Client
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest, UnsupportedMediaType
import traceback
from . import Session
import bcrypt
import jwt
from .mycrypto import rsa_singleton
import datetime

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
        password = bcrypt.hashpw(content['password'].encode(), bcrypt.gensalt())        
        role = content['role']

        new_client = Client(
            username,
            password,
            role
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

        payload = {}
        payload['id'] = user.id
        payload['username'] = username
        payload['service'] = False
        payload['role'] = user.role
        payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        response = jwt.encode(payload, rsa_singleton.get_private_key(), algorithm='RS256')      
    except:
        session.rollback()
        session.close()
        abort(BadRequest.code)

    session.close()
    return response

@app.route('/client/get_public_key', methods=['GET'])
def get_public_key():
    content = {}
    content['public_key'] = rsa_singleton.get_public_key()
    return content    

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


