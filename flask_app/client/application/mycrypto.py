class rsa_singleton(object):
    public_key = 'public'
    private_key = 'private'

    @staticmethod
    def get_public_key():
        return rsa_singleton.public_key
    
    @staticmethod
    def get_private_key():
        return rsa_singleton.private_key 