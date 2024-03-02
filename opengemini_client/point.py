"""
Points module
"""
from abc import ABC
from enum import Enum, auto
import time
from opengemini_client.client import Client


class PrecisionType(Enum):
    """
    define time precision
    """
    PRECISION_NANO_SECOND = auto()
    PRECISION_MICRO_SECOND = auto()
    PRECISION_MILLI_SECOND = auto()
    PRECISION_SECOND = auto()
    PRECISION_MINUTE = auto()
    PRECISION_HOUR = auto()


class Point(Client, ABC):
    """
    Points class
    """

    def __init__(self, measurement: str, precision: PrecisionType, tags: {}, fields: {}):
        self.measurement = measurement
        self.precision = precision
        self.time = time.time()
        self.tags = tags
        self.fields = fields


class BatchPoints(Point, ABC):
    """
    BatchPoints class
    """

    def __init__(self, points: list[Point], measurement: str, precision: PrecisionType, tags: {}, fields: {}):
        super().__init__(measurement, precision, tags, fields)
        self.points = points
