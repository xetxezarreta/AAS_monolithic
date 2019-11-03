class OrderState(object):
    def __init__(self, orderId, userId, pieces):
        self.orderId = orderId
        self.userId = userId
        self.pieces = pieces
        self.p_state = Pending()
        self.d_state = Pending()
    
    def treat_payment(self, message):
        if message['status']:
            self.p_state = Accepted()
        else:
            self.p_state = Cancelled()

    def treat_delivery(self, message):
        if message['status']:
            self.d_state = Accepted()
        else:
            self.d_state = Cancelled()

class State(object):
    def get_state(self):
        return "STATE"

class Pending(State):
    def get_state(self):
        return "PENDING"

class Accepted(State):
    def get_state(self):
        return "ACCEPTED"

class Cancelled(State):
    def get_state(self):
        return "CANCELLED"