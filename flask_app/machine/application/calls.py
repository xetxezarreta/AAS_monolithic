import requests

# Avisa que un pedido está terminado al módulo Order.
def request_order_finished(orderId):
    order_finished = {}
    order_finished['orderId'] = orderId            
    requests.post('http://192.168.17.3:32700/order/notify', json=order_finished)  