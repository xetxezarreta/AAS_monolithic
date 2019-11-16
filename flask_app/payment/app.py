from application import create_app
from application.event_handler import Rabbit

app = create_app()

exchange_name = 'payment_exchange'
Rabbit(exchange_name, 'payment_reserve_queue', Rabbit.payment_reserve)
Rabbit(exchange_name, 'payment_reserve_cancell_queue', Rabbit.payment_reserve_cancell)    

app.app_context().push()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=17000)
