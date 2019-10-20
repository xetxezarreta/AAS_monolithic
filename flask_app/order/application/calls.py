import requests

# Pedir realizar un pago al módulo Payment
def request_payment(userId, number_of_pieces):
    payment = {}
    payment['userId'] = userId
    payment['money'] = 10 * number_of_pieces # 10 por pieza
    payment_response = requests.post('http://192.168.17.3:32700/payment/pay', json=payment).json()
    return payment_response

# Mandar las piezas a fabricar al módulo Machine
def request_pieces_manufacture(orderId, number_of_pieces):
    manufacture_info = {}
    manufacture_info['orderId'] = orderId 
    manufacture_info['number_of_pieces'] = number_of_pieces               
    response = requests.post('http://192.168.17.3:32700/machine/request_piece', json=manufacture_info).json()
    return response

# Manda para generar una nueva entrega al módulo delivery
def request_create_delivery(orderId):
    delivery_info = {}
    delivery_info['orderId'] = orderId
    delivery_info['delivered'] = False
    requests.post('http://192.168.17.3:32700/delivery/create', json=delivery_info).json()

# Mandar para actualizar una entrega ya creada al módulo delivery
def request_update_delivery(orderId):
    delivery_update = {}
    delivery_update['orderId'] = orderId
    delivery_update['delivered'] = True   
    response = requests.post('http://192.168.17.3:32700/delivery/update', json=delivery_update).json()
    return response