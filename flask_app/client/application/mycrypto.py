class rsa_singleton(object):
    private_key = '-----BEGIN PRIVATE KEY-----\nMIGEAgEAMBAGByqGSM49AgEGBS...'
    public_key = '-----BEGIN PUBLIC KEY-----\nMHYwEAYHKoZIzj0CAQYFK4EEAC...'

    @staticmethod
    def get_public_key():
        return rsa_singleton.public_key
    
    @staticmethod
    def get_private_key():
        return rsa_singleton.private_key 