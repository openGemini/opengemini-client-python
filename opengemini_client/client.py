"""
client module
"""
from abc import ABC, abstractmethod

from opengemini_client.models import BatchPoints, QueryResult, Query


class Client(ABC):
    """
    Client abstract class responsible for communicating with the openGemini
    """

    @abstractmethod
    def ping(self, idx: int):
        """
        check that status of cluster
        :param idx:  index
        :return:  return error message
        """

    @abstractmethod
    def query(self, query: Query) -> QueryResult:
        """
        query result
        :param query: Query object
        :return: returns a two-tuple. the first one is the query result and the second is an error message
        """

    @abstractmethod
    def write_batch_points(self, database: str, batch_points: BatchPoints):
        """
        batch points to assigned database
        :param database:  name
        :param batch_points: BatchPoints object
        :return: return an error message
        """

    def create_database(self, database: str):
        """
        create database
        :param database: name
        """
