from os import environ
from dotenv import load_dotenv
import netifaces as ni

# Only needed for developing, on production Docker .env file is used
load_dotenv()


class Config:
    """Set Flask configuration vars from .env file."""
    # Database
    SQLALCHEMY_DATABASE_URI = environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = environ.get("SQLALCHEMY_TRACK_MODIFICATIONS")
    # Consul
    CONSUL_HOST = environ.get("CONSUL_HOST", "192.168.17.16")
    PORT = int(environ.get("PORT", '13000'))
    SERVICE_NAME = environ.get("SERVICE_NAME", "client")
    SERVICE_ID = environ.get("SERVICE_ID", "client")
    IP = None

    __instance = None

    @staticmethod
    def get_instance():
        if Config.__instance is None:
            Config()
        return Config.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if Config.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.get_ip()
            Config.__instance = self

    def get_ip(self):
        ifaces = ni.interfaces()
        if "br-ca1e5a751726" in ifaces:  # this is for my specific iface for debugging.
            self.IP = Config.get_ip_iface("br-ca1e5a751726")
        elif "eth0" in ifaces:  # this is the default interface in docker
            self.IP = Config.get_ip_iface("eth0")
        else:
            self.IP = "127.0.0.1"

    @staticmethod
    def get_ip_iface(iface):
        return ni.ifaddresses(iface)[ni.AF_INET][0]['addr']


