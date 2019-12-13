import requests
from datetime import datetime
from time import sleep
import jwt

class rsa_singleton(object):
    public_key = None

    @staticmethod
    def get_public_key():
        return rsa_singleton.public_key

    @staticmethod
    def request_public_key():
        while rsa_singleton.public_key is None:
            try:
                response = requests.get('https://192.168.17.3:443/client/get_public_key', verify=False).json()
                rsa_singleton.public_key = response['public_key']
            except:
                print('Payment waiting for public key', flush=True)
                sleep(3)
                
    @staticmethod
    def check_jwt(jwt_token):        
        payload = jwt.decode(str.encode(jwt_token), rsa_singleton.public_key, algorithms='RS256')
        # comprobar tiempo de expiración           
        if payload['exp'] < datetime.timestamp(datetime.utcnow()):
            return False
        # comprobar rol
        if payload['role'] != 'ADMIN':
            return False        
        return True
