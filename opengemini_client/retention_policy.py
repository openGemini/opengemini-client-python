"""
Retention Policy module
"""
from abc import ABC
from opengemini_client.client import Client


class RetentionPolicy(Client, ABC):
    """
    # Retention Policy defines the structure of the retention policies used in OpenGemini
    """

    def __init__(self, name: str, duration: str, shard_group_duration: str, hot_duration: str,
                 warm_duration: str, index_duration: str, replica_num: int, is_default: bool):
        self.name = name
        self.duration = duration
        self.shard_group_duration = shard_group_duration
        self.hot_duration = hot_duration
        self.warm_duration = warm_duration
        self.index_duration = index_duration
        self.replica_num = replica_num
        self.is_default = is_default
