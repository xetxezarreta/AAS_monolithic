from application import create_app
from application.event_handler import Rabbit

app = create_app()

exchange_name = 'order_exchange'
Rabbit(exchange_name, 'machine_queue', Rabbit.machine_callback)
Rabbit(exchange_name, 'payment_queue', Rabbit.payment_callback)    
Rabbit(exchange_name, 'delivery_queue', Rabbit.delivery_callback)

app.app_context().push()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=16000)

