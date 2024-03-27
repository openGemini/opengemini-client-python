import ssl
from dataclasses import field, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Union, Optional, List, Any


@dataclass
class Address:
    host: str
    port: int


class AuthType(Enum):
    PASSWORD = 0
    TOKEN = 1


@dataclass
class AuthConfig:
    auth_type: AuthType
    username: str = ''
    password: str = ''
    token: str = ''


@dataclass
class BatchConfig:
    batch_interval: int
    batch_size: int


@dataclass
class Config:
    address: List[Address]
    auth_config: AuthConfig
    batch_config: BatchConfig
    timeout: timedelta
    connection_timeout: timedelta
    gzip_enabled: bool
    tls_enabled: bool
    tls_config: ssl.SSLContext = None


@dataclass
class RetentionPolicy:
    name: str
    duration: str
    shard_group_duration: str
    hot_duration: str
    warm_duration: str
    index_duration: str
    replica_num: int
    is_default: bool


@dataclass
class RpConfig:
    name: str
    duration: str
    shard_group_duration: str
    index_duration: str


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
class Query:
    database: str
    command: str
    retention_policy: str


@dataclass
class SeriesResult:
    series: List[Series] = field(default_factory=list)
    error: str = None


@dataclass
class QueryResult:
    results: List[SeriesResult] = field(default_factory=list)
    error: str = None

    def _has_error(self) -> str:
        if self.error is not None:
            return self.error
        for res in self.results:
            if res.error is not None:
                return res.error
        return ""
