from abc import ABC
from typing import List

from opengemini_client.client import Client
from opengemini_client.models import Config


class ClientImpl(Client, ABC):
    endpoints: List[str]

    def __init__(self, config: Config):
        self.config = config
        protocol = "https://" if config.tls_enabled else "http://"
        self.endpoints = [f"{protocol}{addr.host}:{addr.port}" for addr in config.address]
