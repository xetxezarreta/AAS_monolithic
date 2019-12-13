from datetime import datetime
from .event_publisher import send_log

def create_log(file_name, message):
    log = {
        'date': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        'microservice': 'client',
        'file': file_name,
        'message': message
    }
    send_log(log)