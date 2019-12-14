from datetime import datetime
from .event_publisher import send_log

def create_log(file_name, message):
    log = {
        'microservice': 'client',
        'filename': file_name,
        'message': message
    }
    send_log(log)