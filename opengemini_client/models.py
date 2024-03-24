import io
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


class PrecisionType(Enum):
    PrecisionNanoSecond = 0
    PrecisionMicrosecond = 1
    PrecisionMillisecond = 2
    PrecisionSecond = 3
    PrecisionMinute = 4
    PrecisionHour = 5


def round_datetime(dt: datetime, round_to: timedelta):
    if round_to.seconds == 0:
        microseconds = int(dt.timestamp() * 1000 * 1000)
        rounding = round(microseconds / round_to.microseconds) * round_to.microseconds
        return rounding * 1000
    elif round_to.seconds == 1:
        return round(dt.timestamp()) * 1000 * 1000 * 1000
    else:
        seconds = (dt - dt.min).seconds
        rounding = round(seconds / round_to.seconds) * round_to.seconds
        dt = datetime(dt.year, dt.month, dt.day) + timedelta(seconds=rounding)
        return int(dt.timestamp()) * 1000 * 1000 * 1000


@dataclass
class Point:
    measurement: str
    precision: PrecisionType
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

    def to_string(self) -> str:
        if len(self.measurement) == 0 or len(self.fields) == 0:
            return ""
        writer = io.StringIO()
        writer.write(self.measurement)
        if self.tags is not None:
            writer.write(',')
            writer.write(self.tags_string())
        writer.write(' ')
        writer.write(self.fields_string())
        if self.timestamp is not None:
            writer.write(' ')
            writer.write(self.timestamp_string())
        return writer.getvalue()

    def tags_string(self) -> str:
        writer = io.StringIO()
        first = True
        for k, v in self.tags.items():
            if first is False:
                writer.write(',')
            else:
                first = False
            writer.write(k)
            writer.write('=')
            writer.write(v)
        return writer.getvalue()

    def fields_string(self) -> str:
        writer = io.StringIO()
        first = True
        for k, v in self.fields.items():
            if first is False:
                writer.write(',')
            else:
                first = False
            writer.write(k)
            writer.write('=')
            if type(v) == int:
                writer.write(f"{v}i")
            elif type(v) == str:
                writer.write(f"\"{v}\"")
            elif type(v) == float:
                writer.write(f"{v}")
            elif type(v) == bool:
                if v is True:
                    writer.write('T')
                else:
                    writer.write('F')
        return writer.getvalue()

    def timestamp_string(self) -> str:
        if self.precision == PrecisionType.PrecisionNanoSecond:
            return str(self.timestamp.timestamp() * 1000 * 1000 * 1000)
        elif self.precision == PrecisionType.PrecisionMicrosecond:
            return str(round_datetime(self.timestamp, timedelta(microseconds=1)))
        elif self.precision == PrecisionType.PrecisionMillisecond:
            return str(round_datetime(self.timestamp, timedelta(milliseconds=1)))
        elif self.precision == PrecisionType.PrecisionSecond:
            return str(round_datetime(self.timestamp, timedelta(seconds=1)))
        elif self.precision == PrecisionType.PrecisionMinute:
            return str(round_datetime(self.timestamp, timedelta(minutes=1)))
        elif self.precision == PrecisionType.PrecisionHour:
            return str(round_datetime(self.timestamp, timedelta(hours=1)))
        else:
            return ""


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
