from application import create_app
from application.event_handler import Rabbit
from application import create_app
from application.event_handler import Rabbit

app = create_app()

exchange_name = 'delivery_exchange'
Rabbit(exchange_name, 'delivery_create_queue', Rabbit.delivery_create)
Rabbit(exchange_name, 'delivery_cancell_queue', Rabbit.delivery_cancell)    
Rabbit(exchange_name, 'delivery_update_queue', Rabbit.delivery_update)
    
app.app_context().push()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=14000)
