"""
client module
"""
from abc import ABC, abstractmethod

import client_impl
from point import BatchPoints
from query import Query
from query_result import QueryResult
from rentention_policy import RetentionPolicy


class Address:
    """
    Address configuration for providing service
    """

    def __init__(self, host: str, port: int):
        """
        :param host: service ip or domain.
        :param port: exposed service port
        """
        self.host = host
        self.port = port


class AuthType:
    """
    AuthType represents the type of identity authentication
    """
    AUTH_TYPE_PASSWORD = 0
    AUTH_TYPE_TOKE = 1


class AuthConfig:
    """
    AuthConfig represents the configuration for authentication
    """

    def __init__(self, auth_type: AuthType, username: str, password: str, token: str) -> None:
        """

        :param auth_type: AuthType represents the type of identity authentication
        :param username: provided username when  AuthTypePassword is used
        :param password:  provided password when  AuthTypePassword is used
        :param token: provided token when  AuthTypeToken is used
        """
        self.auth_type = auth_type
        self.username = username
        self.password = password
        self.token = token


class BatchConfig:
    """
    BatchConfig represents the configuration for batch processing
    """

    def __init__(self, batch_interval: int, batch_size: int):
        """
        :param batch_interval: batch time interval that triggers batch processing.(unit: ms)
        :param batch_size: batch size that triggers batch processing.
        """
        self.batch_interval = batch_interval
        self.batch_size = batch_size


class RpCconfig:
    """
    RpCconfig represents the configuration for retention policy
    """

    def __init__(self, name: str, duration: str, shard_group_duration: str, index_duration: str):
        """
        :param name: retention policy name
        :param duration: indicates how long the data will be retained
        :param shard_group_duration: determines the time range for sharding groups
        :param index_duration: determines the time range of the index group
        """
        self.name = name
        self.duration = duration
        self.shard_group_duration = shard_group_duration
        self.index_duration = index_duration


class Config:
    """
     configuration of the service URL for the openGemini service
    """

    def __init__(self, address: list[Address], auth_config: AuthConfig, batch_config: BatchConfig,
                 timeout, connection_timeout, gzip_enabled: bool, tls_enabled: bool,
                 tls_config: bool):
        """
        :param address: This parameter is required
        :param auth_config: AuthConfig configration information for authentication
        :param batch_config: BatchConfig configration information for batch processing
        :param timeout: default 30s
        :param connection_timeout:  ConnectionTimeout default 10s
        :param gzip_enabled: determines whether to use gzip compression for data transmission
        :param tls_enabled: determines whether to use TLS encryption for data transmission
        :param tls_config: configration information for tls authentication
        """
        self.address = address
        self.auth_config = auth_config
        self.batch_config = batch_config
        self.timeout = timeout
        self.connection_timeout = connection_timeout
        self.gzip_enabled = gzip_enabled
        self.tls_enabled = tls_enabled
        self.tls_config = tls_config


class Client(ABC):
    """
    Client abstract class responsible for communicating with the openGemini
    """

    @abstractmethod
    def ping(self, idx: int) -> str:
        """
        check that status of cluster
        :param idx:
        :return:
        """

    @abstractmethod
    def query(self, query: Query) -> tuple[QueryResult, str]:
        """
        query result
        :param query: Qu
        :return: returns a two-tuple. the first one is the query result and the second is an error message
        """

    @abstractmethod
    def create_database(self, database: str) -> str:
        """
        create database
        :param database:  name
        :return: return an error message of string type
        """

    @abstractmethod
    def create_database_with_rp(self, database: str, rp_config: RpCconfig) -> str:
        """
        create database with retention policy
        :param database: database need to create
        :param rp_config: confi
        :return: return an error message of string type
        """

    @abstractmethod
    def show_database(self, string: list, error: str) -> None:
        """
        show database
        :param string:  list of type String
        :param error:  error
        :return: no return value
        """

    @abstractmethod
    def drop_database(self, database: str) -> str:
        """
        drop database
        :param database: database name
        :return: return an error message of string type
        """

    @abstractmethod
    def create_retention_policy(self, database: str, rp_config: RpCconfig, is_default: bool) -> str:
        """
        create retention policy
        :param database: database name
        :param rp_config: configuration information for retention policy
        :param is_default: set the new retention policy as the default retention policy for the database
        :return: return an error message of string type
        """

    @abstractmethod
    def show_retention_policy(self, database: str) -> tuple[list[RetentionPolicy], str]:
        """
        show retention policy
        :param database: database name
        :return: return a two-tuple. the first one is a list whose elements are the retention policy
         and the second is an error message
        """


def new_client(config: Config) -> Client:
    return client_impl.new_client(config)
