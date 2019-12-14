from os import environ
from dotenv import load_dotenv

# Only needed for developing, on production Docker .env file is used
load_dotenv()


class Config:
    """Set Flask configuration vars from .env file."""
    # Database
    SQLALCHEMY_DATABASE_URI = environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = environ.get("SQLALCHEMY_TRACK_MODIFICATIONS")
    # Consul
    CONSUL_HOST = environ.get("CONSUL_HOST", "192.168.17.5")
    PORT = int(environ.get("PORT", '13000'))
    SERVICE_NAME = environ.get("SERVICE_NAME", "client")
    SERVICE_ID = environ.get("SERVICE_ID", "client")
    IP = None

