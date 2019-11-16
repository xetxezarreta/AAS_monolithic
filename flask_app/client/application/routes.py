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
import json

# Client Routes #########################################################################################################
@app.route('/client/create', methods=['POST'])
def create_client():
    session = Session()
    new_client= None
    if request.headers['Content-Type'] != 'application/json':
        abort(UnsupportedMediaType.code)
    content = request.json
    try:
        new_client = Client(
            username = content['username'],
            password = bcrypt.hashpw(content['password'].encode(), bcrypt.gensalt()).decode('utf-8'),
            role = content['role']
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
        user = session.query(Client).filter(Client.id == content['id']).one()
        if not bcrypt.checkpw(content['password'].encode('utf-8'), user.password.encode('utf-8')):
            raise Exception
        payload = {}
        payload['id'] = user.id
        payload['username'] = user.username
        payload['service'] = False
        payload['role'] = user.role
        payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        print('44444444444444444', flush=True)
        response = {}
        response['jwt'] = jwt.encode(payload, rsa_singleton.get_private_key(), algorithm='RS256')  
        print('55555555555555555', flush=True)
    except:
        session.rollback()
        session.close()
        abort(BadRequest.code)
    print('666666666666666666', flush=True)
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


