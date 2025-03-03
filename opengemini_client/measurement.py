# Copyright 2025 openGemini Authors
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
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict

ErrEmptyDatabaseName = "empty database name"
ErrEmptyMeasurement = "empty measurement"
ErrEmptyTagOrField = "empty tag or field"
ErrEmptyIndexList = "empty index list"


class FieldType(Enum):
    FieldTypeInt64 = "INT64"
    FieldTypeFloat64 = "FLOAT64"
    FieldTypeString = "STRING"
    FieldTypeBool = "BOOL"


class ShardType(Enum):
    ShardTypeHash = "HASH"
    ShardTypeRange = "RANGE"


class IndexType(Enum):
    IndexTypeText = "text"


class EngineType(Enum):
    EngineTypeColumnstore = "columnstore"


class ComparisonOperator(Enum):
    Equals = "="
    NotEquals = "<>"
    GreaterThan = ">"
    LessThan = "<"
    GreaterThanOrEquals = ">="
    LessThanOrEquals = "<="
    Match = "=~"
    NotMatch = "!~"


@dataclass
class Measurement:
    database: str
    measurement: str
    retention_policy: str
    # specify tag list to create measurement
    tags: List[str] = field(default_factory=list)
    # specify field map to create measurement
    fields: Dict[str, FieldType] = field(default_factory=dict)
    # specify shard type to create measurement, support ShardTypeHash and ShardTypeRange two ways to
    # break up data, required when use high series cardinality storage engine(HSCE)
    shard_type: ShardType = None
    # specify shard keys(tag as partition key) to create measurement, required when use
    # high series cardinality storage engine(HSCE)
    shard_keys: List[str] = field(default_factory=list)
    # FullTextIndex required when want measurement support full-text index
    index_type: IndexType = None
    # required when specify which Field fields to create a full-text index on,
    # these fields must be 'string' data type
    index_list: List[str] = field(default_factory=list)
    # required when want measurement support HSCE, set EngineTypeColumnStore
    engine_type: EngineType = None
    # required when use HSCE, such as the primary key is `location` and `direction`, which means that the
    # storage engine will create indexes on these two fields
    primary_keys: List[str] = field(default_factory=list)
    # required when use HSCE, specify the data sorting method inside the storage engine, time means sorting
    # by time, and can also be changed to rtt or direction, or even other fields in the table
    sort_keys: List[str] = field(default_factory=list)

    def check(self):
        if len(self.database) == 0:
            raise ValueError(ErrEmptyDatabaseName)
        if len(self.measurement) == 0:
            raise ValueError(ErrEmptyMeasurement)
        if len(self.tags) == 0 and len(self.fields) == 0:
            raise ValueError(ErrEmptyTagOrField)
        if self.index_type is not None and len(self.index_list) == 0:
            raise ValueError(ErrEmptyIndexList)

    def _write_tags_fields(self, writer: io.StringIO):
        writer.write(f"CREATE MEASUREMENT {self.measurement} (")
        if len(self.tags) != 0:
            tags = []
            for tag in self.tags:
                tags.append(f"{tag} TAG")
            writer.write(",".join(tags))
        if len(self.tags) != 0 and len(self.fields) != 0:
            writer.write(",")
        if len(self.fields) != 0:
            fields = []
            for key, value in self.fields.items():
                fields.append(f"{key} {value.value} FIELD")
            writer.write(",".join(fields))
        writer.write(")")

    def _write_index(self, writer: io.StringIO):
        writer.write(" WITH ")
        writer.write(f" INDEXTYPE {self.index_type.value}")
        writer.write(" INDEXLIST " + ",".join(self.index_list))

    def _writer_other(self, writer: io.StringIO):
        with_identifier = False
        if self.engine_type is not None:
            with_identifier = True
            writer.write(" WITH ")
            writer.write(f" ENGINETYPE = {self.engine_type.value}")
        if len(self.shard_keys) != 0:
            if with_identifier is False:
                with_identifier = True
                writer.write(" WITH ")
            writer.write(" SHARDKEY " + ",".join(self.shard_keys))
        if self.shard_type is not None:
            if with_identifier is False:
                with_identifier = True
                writer.write(" WITH ")
            writer.write(f" TYPE {self.shard_type.value}")
        if len(self.primary_keys) != 0:
            if with_identifier is False:
                with_identifier = True
                writer.write(" WITH ")
            writer.write(" PRIMARYKEY " + ",".join(self.primary_keys))
        if len(self.sort_keys) != 0:
            if with_identifier is False:
                writer.write(" WITH ")
            writer.write(" SORTKEY " + ",".join(self.sort_keys))

    def to_string(self) -> str:
        writer = io.StringIO()
        self._write_tags_fields(writer)

        if self.index_type is not None:
            self._write_index(writer)
            return writer.getvalue()

        self._writer_other(writer)
        return writer.getvalue()


@dataclass
class MeasurementCondition:
    database: str
    Operator: ComparisonOperator = None
    Value: str = ''

    def check(self):
        if len(self.database) == 0:
            raise ValueError(ErrEmptyDatabaseName)

    def to_string(self) -> str:
        writer = io.StringIO()
        writer.write("SHOW MEASUREMENTS")
        if self.Operator is not None:
            writer.write(f" WITH MEASUREMENT {self.Operator.value} {self.Value}")
        return writer.getvalue()
