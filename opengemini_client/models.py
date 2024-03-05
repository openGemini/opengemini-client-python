from dataclasses import field, dataclass
from datetime import datetime
from typing import Dict, Union, Optional, List, Any


@dataclass
class Address:
    host: str
    port: int


@dataclass
class Point:
    measurement: str
    fields: Dict[str, Union[str, int, float, bool]]
    tags: Dict[str, str] = field(default_factory=dict)
    timestamp: Optional[datetime] = None

    def add_tag(self, key: str, value: str):
        self.tags[key] = value

    def add_field(self, key: str, value: Union[str, int, float, bool]):
        self.fields[key] = value

    def set_time(self, time: datetime):
        self.timestamp = time

    def set_measurement(self, name: str):
        self.measurement = name


@dataclass
class BatchPoints:
    points: List[Point] = field(default_factory=list)


@dataclass
class Series:
    name: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    columns: List[str] = field(default_factory=list)
    values: List[List[Any]] = field(default_factory=list)


@dataclass
class SeriesResult:
    series: List[Series] = field(default_factory=list)
    error: str = ""


@dataclass
class Query:
    database: str
    command: str
    retention_policy: str


@dataclass
class QueryResult:
    results: List[SeriesResult] = field(default_factory=list)
    error: str = ""
