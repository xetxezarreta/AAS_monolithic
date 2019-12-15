from .config import Config
from flask_consulate import Consul
from flask import Flask
import dns

config = Config.get_instance()
consul_resolver = dns.resolver.Resolver(configure=False)
consul_resolver.port = 8600
consul_resolver.nameservers = [config.CONSUL_HOST]

class BLConsul:
    __instance = None
    consul = None

    @staticmethod
    def get_instance():
        if BLConsul.__instance is None:
            BLConsul()
        return BLConsul.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if BLConsul.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            BLConsul.__instance = self

    def init_and_register(self, app):
        self.consul = Consul(app=app)
        self.register_service()

    def register_service(self):
        try:
            self.consul.register_service(
                service_id=config.SERVICE_ID,
                name=config.SERVICE_NAME,
                interval='10s',
                tags=['flask', 'microservice', 'aas'],
                port=config.PORT,
                address=config.IP,
                httpcheck='http://{host}:{port}/{service_name}/health'.format(
                    host=config.IP,
                    port=config.PORT,
                    service_name=config.SERVICE_NAME
                )
            )      
        except Exception as e:
            print(e, flush=True)
    
    def get_service(self, service_name):
        ret = {
            "Address": None,
            "Port": None
        }
        try:
            srv_results = consul_resolver.query("{}.service.consul".format(service_name), "srv")  # SRV DNS query
            srv_list = srv_results.response.answer  # PORT - target_name relation
            a_list = srv_results.response.additional  # IP - target_name relation

            # DNS returns a list of replicas, supposedly sorted using Round Robin. We always get the 1st element: [0]
            srv_replica = srv_list[0][0]
            port = srv_replica.port
            target_name = srv_replica.target

            # From all the IPs, get the one with the chosen target_name
            for a in a_list:
                if a.name == target_name:
                    ret['Address'] = a[0]
                    ret['Port'] = port
                    break

        except dns.exception.DNSException as e:
            print("Could not get service url: {}".format(e))
        return ret

    # Get Key Values from Consul's key store
    def get_key_value_items(self):
        return self.consul.session.kv.items()

    def get_service_catalog(self):
        return self.consul.session.catalog.services()

    def get_service_replicas(self):
        return self.consul.session.agent.services()
