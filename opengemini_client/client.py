"""
client module
"""
from abc import ABC, abstractmethod
from typing import List

from opengemini_client.models import BatchPoints, QueryResult, Query, RpConfig, ValuesResult


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

    @abstractmethod
    def create_database(self, database: str, rp: RpConfig = None):
        """
        create database
        :param rp: RpConfig
        :param database: name
        """

    @abstractmethod
    def show_databases(self) -> List[str]:
        """
        show databases
        :return: returns a databases list.
        """

    @abstractmethod
    def drop_database(self, database: str):
        """
        drop database
        :param database: name
        """

    @abstractmethod
    def create_retention_policy(self, dbname, rp_config: RpConfig, is_default: bool):
        pass

    @abstractmethod
    def show_retention_policies(self, dbname):
        pass

    @abstractmethod
    def drop_retention_policy(self, dbname, retention_policy: str):
        pass

    @abstractmethod
    def show_tag_keys(self, database, command: str) -> List[ValuesResult]:
        """
        show tag keys
        :param database: name
        :param command: show tag keys query command
        :return ValuesResult: query results
        """

    @abstractmethod
    def show_tag_values(self, database, command: str) -> List[ValuesResult]:
        """
        show tag values
        :param database: name
        :param command: show tag values query command
        :return ValuesResult: query results
        """

    @abstractmethod
    def show_field_keys(self, database, command: str) -> List[ValuesResult]:
        """
        show field keys
        :param database: name
        :param command: show field keys query command
        :return ValuesResult: query results
        """

    @abstractmethod
    def show_series(self, database, command: str) -> List[str]:
        """
        show series
        :param database: name
        :param command: show series query command
        :return ValuesResult: query results
        """
