from flask import request, jsonify, abort
from flask import current_app as app
from .models import Piece
from werkzeug.exceptions import NotFound, InternalServerError, BadRequest, UnsupportedMediaType
import traceback
from .machine import Machine
from . import Session

my_machine = Machine()

# Machine Routes #######################################################################################################
# Obtiene la pieza y la cantidad que tiene que fabricar.
# Devuelve 'true' si se han añadido piezas.
# Devuelve 'false' si no se han añadido piezas.
#{
#    "number_of_pieces": 3,
#    "orderId": 1
#}
@app.route('/machine/request_piece', methods=['POST'])
def request_piece_mannufacturing():
    session = Session()
    if request.headers['Content-Type'] != 'application/json':
        abort(UnsupportedMediaType.code)
    content = request.json
    status = False
    try:
        number_of_pieces = content['number_of_pieces']
        orderId = content['orderId']

        pieces_list = list()
        for _ in range(number_of_pieces):
            piece = Piece()
            piece.orderId = orderId            
            session.add(piece)    
            session.commit()     
            session.refresh(piece)
            print(piece)      
            pieces_list.append(piece)

        if pieces_list: # miramos si hay elemento en la lista.
            my_machine.add_pieces_to_queue(pieces_list)
            status = True
        
    except KeyError:
        session.rollback()
        session.close()
        abort(BadRequest.code)

    response = get_machine_response(status)
    session.close()
    return response

@app.route('/machine/status', methods=['GET'])
def view_machine_status():
    working_piece = my_machine.working_piece
    queue = my_machine.queue
    if working_piece:
        working_piece = working_piece.as_dict()
    response = {"status": my_machine.status, "working_piece": working_piece, "queue": list(queue)}
    return jsonify(response)

# Respuesta del POST del machine.
# Si la operación es correcta, status=True
# Si la operación no es correcta, status=False
# EJEMPLO:
#{
#    "status": true
#}
def get_machine_response(status):
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


