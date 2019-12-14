from application import create_app
from application.event_handler import Rabbit
from application.auth import rsa_singleton

app = create_app()

# create rabbitmq queues
Rabbit('machine_exchange', 'machine_queue_response', Rabbit.machine_response)
Rabbit('payment_exchange', 'sagas_payment_queue', Rabbit.payment_response)
Rabbit('delivery_exchange', 'sagas_delivery_queue', Rabbit.delivery_response)

# request jwt public key
rsa_singleton.request_public_key()

app.app_context().push()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=16000)

