from application import create_app
from application.event_handler import Rabbit
from application.auth import rsa_singleton

app = create_app()
Rabbit('machine_exchange', 'machine_queue', Rabbit.machine_callback)

# request jwt public key
#rsa_singleton.request_public_key()

app.app_context().push()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=15000)
