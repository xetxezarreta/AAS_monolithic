class OrderState(object):
    def __init__(self, orderId, userId, pieces):
        self.orderId = orderId
        self.userId = userId
        self.pieces = pieces
        self.state = Pending_payment()
    
    def treat_payment(self, message):
        if message['status']:
            self.state = Pending_delivery()
        else:
            self.state = Cancelled_payment()

    def treat_delivery(self, message):
        if message['status']:
            self.state = Accepted_delivery()
        else:
            self.state = Cancelled_delivery()

class State(object):
    def get_state(self):
        return "STATE"

class Pending_payment(State):
    def get_state(self):
        return "PENDING PAYMENT"

class Cancelled_payment(State):
    def get_state(self):
        return "CANCELLED PAYMENT"

class Pending_delivery(State):
    def get_state(self):
        return "PENDING DELIVERY"

class Accepted_delivery(State):
    def get_state(self):
        return "ACCEPTED DELIVERY"

class Cancelled_delivery(State):
    def get_state(self):
        return "CANCELLED DELIVERY"
