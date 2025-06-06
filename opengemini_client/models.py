# Copyright 2024 openGemini Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import io
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
class TlsConfig:
    cert_file: str = ''
    key_file: str = ''
    ca_file: str = ''


@dataclass
class BatchConfig:
    batch_interval: int
    batch_size: int


@dataclass
class GrpcConfig:
    address: List[Address]
    auth_config: AuthConfig = None
    tls_enable: bool = False
    tls_config: TlsConfig = None


@dataclass
class Config:
    address: List[Address]
    batch_config: BatchConfig = None
    timeout: timedelta = None
    connection_timeout: timedelta = None
    gzip_enabled: bool = False
    tls_enabled: bool = False
    auth_config: AuthConfig = None
    tls_config: TlsConfig = None
    grpc_config: GrpcConfig = None


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


class Precision(Enum):
    PrecisionNanoSecond = 0
    PrecisionMicrosecond = 1
    PrecisionMillisecond = 2
    PrecisionSecond = 3
    PrecisionMinute = 4
    PrecisionHour = 5

    def epoch(self) -> str:
        if self == Precision.PrecisionNanoSecond:
            unit = 'ns'
        elif self == Precision.PrecisionMicrosecond:
            unit = 'u'
        elif self == Precision.PrecisionMillisecond:
            unit = 'ms'
        elif self == Precision.PrecisionSecond:
            unit = 's'
        elif self == Precision.PrecisionMinute:
            unit = 'm'
        elif self == Precision.PrecisionHour:
            unit = 'h'
        else:
            unit = ''
        return unit


def round_datetime(dt: datetime, round_to: timedelta):
    if round_to.seconds == 0:
        microseconds = int(dt.timestamp() * 1000 * 1000)
        rounding = round(microseconds / round_to.microseconds) * round_to.microseconds
        rd = rounding * 1000
    elif round_to.seconds == 1:
        rd = round(dt.timestamp()) * 1000 * 1000 * 1000
    else:
        seconds = (dt - dt.min).seconds
        rounding = round(seconds / round_to.seconds) * round_to.seconds
        dt = datetime(dt.year, dt.month, dt.day) + timedelta(seconds=rounding)
        rd = int(dt.timestamp()) * 1000 * 1000 * 1000
    return rd


def chars_to_escape(writer: io.StringIO, s: str, escape_str: str):
    for i, c in enumerate(s):
        need_escape = c in escape_str
        need_check_next_char = c == '\\' and i < len(s) - 1
        if not need_escape and need_check_next_char:
            next_char = s[i + 1]
            need_escape = next_char == '\\' or next_char in escape_str
        if need_escape:
            writer.write('\\')
        writer.write(s[i])


@dataclass
class Point:
    measurement: str
    precision: Precision
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
        with io.StringIO() as writer:
            self.write_measurement(writer)
            self.write_tags(writer)
            self.write_fields(writer)
            self.write_timestamp(writer)
            res = writer.getvalue()
        return res

    def write_measurement(self, writer: io.StringIO):
        chars_to_escape(writer, self.measurement, ', ')

    def write_tags(self, writer: io.StringIO):
        if self.tags is None:
            return
        for k, v in self.tags.items():
            writer.write(',')
            chars_to_escape(writer, k, ', =')
            writer.write('=')
            chars_to_escape(writer, v, ', =')

    def write_fields(self, writer: io.StringIO):
        sep = ' '
        for k, v in self.fields.items():
            writer.write(sep)
            sep = ','
            chars_to_escape(writer, k, ', =')
            writer.write('=')
            if isinstance(v, int):
                writer.write(f"{v}i")
            elif isinstance(v, str):
                writer.write('"')
                chars_to_escape(writer, v, '"')
                writer.write('"')
            elif isinstance(v, float):
                writer.write(f"{v}")
            elif isinstance(v, bool):
                if v:
                    writer.write('T')
                else:
                    writer.write('F')

    def generate_timestamp(self):
        ts = 0
        if self.timestamp is None:
            return ts
        if self.precision == Precision.PrecisionMicrosecond:
            ts = round_datetime(self.timestamp, timedelta(microseconds=1))
        elif self.precision == Precision.PrecisionMillisecond:
            ts = round_datetime(self.timestamp, timedelta(milliseconds=1))
        elif self.precision == Precision.PrecisionSecond:
            ts = round_datetime(self.timestamp, timedelta(seconds=1))
        elif self.precision == Precision.PrecisionMinute:
            ts = round_datetime(self.timestamp, timedelta(minutes=1))
        elif self.precision == Precision.PrecisionHour:
            ts = round_datetime(self.timestamp, timedelta(hours=1))
        else:
            ts = self.timestamp.timestamp() * 1000 * 1000 * 1000
        return ts

    def write_timestamp(self, writer: io.StringIO):
        if self.timestamp is None:
            return
        writer.write(' ')
        writer.write(str(self.generate_timestamp()))


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
    precision: Precision = Precision.PrecisionNanoSecond


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


@dataclass
class ValuesResult:
    measurement: str
    values: List[Any]


@dataclass
class KeyValue:
    name: str
    value: str
