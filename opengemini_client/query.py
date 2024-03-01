"""
# Query module
"""
from abc import ABC
from opengemini_client.client import Client


class Query(Client, ABC):
    """
    # Query class
    """

    def __init__(self, database: str, command: str, retention_policy: str):
        self.database = database
        self.command = command
        self.retention_policy = retention_policy


class KeyValue:
    def __init__(self, name, value):
        self.name = name
        self.value = value
