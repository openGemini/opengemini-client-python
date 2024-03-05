from abc import ABC
from opengemini_client.client import Client
from opengemini_client.models import Config, Endpoint
from opengemini_client.utils import AtomicInt


class ClientImpl(Client, ABC):
    """
    OpenGemini client class
    """

    def __init__(self, config: Config, endpoints: list[Endpoint]):
        """
        OpenGemini client
        :param config:  config object
        :param endpoints:  urls
        """
        self.config = config
        self.endpoints = endpoints
        self.prev_idx = AtomicInt(5)
        self.data_chan = {}
