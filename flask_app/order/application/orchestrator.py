from .event_publisher import send_message

class Orchestrator(object):    
    def __init__(self):
        self.order_state_list = list()
    
    def treat_message(self, message):
        order_state = self.__get_order_from_list(message['orderId'])
        if message['type'] == 'PAYMENT':
            order_state.treat_payment(message)
            if order_state.state.get_state() == 'PENDING DELIVERY':
                send_message("delivery_exchange", "delivery_create_queue", message)

        if message['type'] == 'DELIVERY':
            order_state.treat_delivery(message)
            if order_state.state.get_state() == 'ACCEPTED DELIVERY':     
                print(type(message), flush=True)    
                send_message("machine_exchange", "machine_queue", message)
            else:
                send_message("payment_exchange", "payment_reserve_cancell_queue", message)
            self.order_state_list.remove(order_state)
    
    def __get_order_from_list(self, orderId):
        for order_state in self.order_state_list:
            if order_state.orderId == orderId:
                return order_state
        return None

orchestrator = Orchestrator()

def get_orchestrator():
    return orchestrator
