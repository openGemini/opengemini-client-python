
"""
client module
"""
from abc import ABC,abstractmethod

import client_impl
from point import BatchPoints
from query import Query
from query_result import QueryResult
from rentention_policy import RetentionPolicy


class Address:
    """
    Address configuration for providing service
    """

    def __init__(self,host: str, port: int):
        """
        :param host: service ip or domain.
        :param port: exposed service port
        """
        self.host = host
        self.port = port

class AuthType:
    """
    AuthType reprensents the type of identity authentication
    """
    AUTH_TPYE_PASSWORD = 0
    AUTH_TPYE_TOKE = 1