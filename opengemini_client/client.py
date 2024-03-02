"""
client module
"""
from abc import ABC, abstractmethod
from opengemini_client.common import RpCconfig
from opengemini_client.point import BatchPoints
from opengemini_client.query import Query
from opengemini_client.retention_policy import RetentionPolicy


class Client(ABC):
    """
    Client abstract class responsible for communicating with the openGemini
    """

    @abstractmethod
    def ping(self, idx: int) -> str:
        """
        check that status of cluster
        :param idx:  index
        :return:  return error message
        """

    @abstractmethod
    def query(self, query: Query) -> tuple[Query, str]:
        """
        query result
        :param query: query object
        :return: returns a two-tuple. the first one is the query result and the second is an error message
        """

    @abstractmethod
    def write_batch_points(self, database: str, batch_points: BatchPoints) -> str:
        """
        batch points to assigned database
        :param database:  name
        :param batch_points: Batch points object
        :return: return an error message
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
        :param database:  name
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