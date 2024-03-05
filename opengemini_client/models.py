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


@dataclass
class Query:
    database: str
    command: str
    retention_policy: str


@dataclass
class Address:
    host: str
    port: int


@dataclass
class AuthType:
    AUTH_TYPE_PASSWORD: int = 0
    AUTH_TYPE_TOKE: int = 1


@dataclass
class AuthConfig:
    auth_type: AuthType
    username: str
    password: str
    token: str


@dataclass
class BatchConfig:
    batch_interval: int
    batch_size: int


@dataclass
class RpCconfig:
    name: str
    duration: str
    shard_group_duration: str
    index_duration: str


@dataclass
class Config:
    address: List[Address]
    auth_config: AuthConfig
    batch_config: BatchConfig
    timeout: int
    connection_timeout: int
    gzip_enabled: bool
    tls_enabled: bool
    tls_config: bool


@dataclass
class Endpoint:
    url: str


@dataclass
class RequestDetails:
    query_values: str
    headers: Dict[str, str]
    body: Any
