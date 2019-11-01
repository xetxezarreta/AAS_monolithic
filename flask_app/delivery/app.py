from application import create_app
from application.event_handler import Rabbit

app = create_app()
Rabbit()
app.app_context().push()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=14000)
