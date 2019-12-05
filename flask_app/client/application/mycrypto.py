from Crypto.PublicKey import RSA

key = RSA.generate(2048)
private_key = key.export_key()#.replace(b'RSA ', b'')
public_key = key.publickey().export_key()#.replace(b'RSA ', b'')

class rsa_singleton(object):
    @staticmethod
    def get_public_key():        
        return public_key
    
    @staticmethod
    def get_private_key():
        return private_key