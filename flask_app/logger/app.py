from application import create_app
from application.event_handler import Rabbit
from application.auth import rsa_singleton

app = create_app()

# create rabbitmq queues
exchange_name = 'logger_exchange'
Rabbit(exchange_name, 'logger_queue', Rabbit.log_create)

# request jwt public key
rsa_singleton.request_public_key()
    
app.app_context().push()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=18000)
