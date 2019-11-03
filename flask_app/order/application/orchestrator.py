from .event_publisher import send_message

class Orchestrator(object):    
    def __init__(self):
        self.order_state_list = list()
    
    def treat_message(self, message):
        order_state = self.__get_order_from_list(message['orderId'])

        if message['type'] == 'PAYMENT':
            order_state.treat_payment(message)
        else:
            order_state.treat_delivery(message)
        
        if order_state.p_state.get_state() == 'ACCEPTED' and order_state.d_state.get_state() == 'ACCEPTED':
            send_message("machine_exchange", "machine_queue", message)
        elif order_state.p_state.get_state() == 'CANCELLED' or order_state.d_state.get_state() == 'CANCELLED':
            send_message("payment_exchange", "payment_reserve_cancell_queue", message)
            send_message("delivery_exchange", "delivery_cancell_queue", message)
            self.order_state_list.remove(order_state)
    
    def __get_order_from_list(self, orderId):
        for order_state in self.order_state_list:
            if order_state.orderId == orderId:
                return order_state
        return None

orchestrator = Orchestrator()

def get_orchestrator():
    return orchestrator
