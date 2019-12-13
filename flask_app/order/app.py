from application import create_app
from application.event_handler import Rabbit
from application.auth import rsa_singleton

app = create_app()

# create rabbitmq queues
exchange_name = 'order_exchange'
Rabbit(exchange_name, 'machine_queue', Rabbit.machine_callback)
Rabbit(exchange_name, 'sagas_payment_queue', Rabbit.sagas_payment_callback)
Rabbit(exchange_name, 'sagas_delivery_queue', Rabbit.sagas_delivery_callback)

# request jwt public key
rsa_singleton.request_public_key()

app.app_context().push()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=16000)

