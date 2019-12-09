<<<<<<< HEAD
from application import create_app
from application.event_handler import Rabbit

app = create_app()

exchange_name = 'client_exchange'
Rabbit(exchange_name, 'client_get_public_key')

app.app_context().push()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=13000)
=======
from application import create_app

app = create_app()
app.app_context().push()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=13000)
>>>>>>> f7c5b0da40c8339f5130b3a81aa2cb5e619a6882
