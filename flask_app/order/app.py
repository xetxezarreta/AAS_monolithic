from application import create_app
from application.event_handler import Rabbit

app = create_app()

exchange_name = 'order_exchange'
Rabbit(exchange_name, 'machine_queue', Rabbit.machine_callback)
Rabbit(exchange_name, 'sagas_payment_queue', Rabbit.sagas_payment_callback)
Rabbit(exchange_name, 'sagas_delivery_queue', Rabbit.sagas_delivery_callback)

app.app_context().push()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=16000)
