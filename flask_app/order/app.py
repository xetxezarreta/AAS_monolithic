<<<<<<< HEAD
from application import create_app
from application.event_handler import Rabbit
from application.myjwt import rsa_singleton

app = create_app()

# create rabbitmq queues
exchange_name = 'order_exchange'
Rabbit(exchange_name, 'machine_queue', Rabbit.machine_callback)
Rabbit(exchange_name, 'sagas_queue', Rabbit.sagas_callback)

# request jwt public key
rsa_singleton.request_public_key()

app.app_context().push()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=16000)

=======
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

>>>>>>> f7c5b0da40c8339f5130b3a81aa2cb5e619a6882
