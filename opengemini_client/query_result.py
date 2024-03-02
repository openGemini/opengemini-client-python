"""
RetentionPolicy module
"""

from abc import ABC

from opengemini_client.client import Client
from opengemini_client.common import SeriesResult


class QueryResult(Client, ABC):
    """
    QueryResult class
    """

    def __init__(self, results: list[SeriesResult], error: str):
        self.results = results
        self.error = error

    def has_error(self):
        if len(self.error) > 0:
            return self.error
        for result in self.results:
            if len(result.error) > 0:
                return result.error

        return None
