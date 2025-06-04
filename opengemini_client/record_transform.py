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

from dataclasses import dataclass, field
from typing import Dict, Union

from opengemini_client.models import Point
from opengemini_client.record.colval import ColVal
from opengemini_client.record.field import Field, Field_Type_Int, Field_Type_Float, Field_Type_Boolean, \
    Field_Type_String, Field_Type_Tag
from opengemini_client.record.record import TimeField, Record

err_invalid_field_value = ValueError("invalid field value type")
err_empty_record = ValueError("empty record")


def get_field_type(v):
    if isinstance(v, int):
        t = Field_Type_Int
    elif isinstance(v, float):
        t = Field_Type_Float
    elif isinstance(v, bool):
        t = Field_Type_Boolean
    elif isinstance(v, str):
        t = Field_Type_String
    else:
        raise err_invalid_field_value
    return t


@dataclass
class Column:
    field: Field
    col: ColVal

    def add_nulls(self, row_count):
        if self.field.Type in (Field_Type_String, Field_Type_Tag):
            self.col.append_string_nulls(row_count)
        elif self.field.Type == Field_Type_Int:
            self.col.append_integer_nulls(row_count)
        elif self.field.Type == Field_Type_Float:
            self.col.append_float_nulls(row_count)
        elif self.field.Type == Field_Type_Boolean:
            self.col.append_boolean_nulls(row_count)
        else:
            raise err_invalid_field_value

    def add_value(self, value):
        if self.field.Type in (Field_Type_String, Field_Type_Tag):
            self.col.append_string(value)
        elif self.field.Type == Field_Type_Int:
            self.col.append_integer(value)
        elif self.field.Type == Field_Type_Float:
            self.col.append_float(value)
        elif self.field.Type == Field_Type_Boolean:
            self.col.append_boolean(value)
        else:
            raise err_invalid_field_value


@dataclass
class RecordTransform:
    row_count: int = 0
    min_time: int = 0
    max_time: int = 0
    columns: Dict[str, Column] = field(default_factory=dict)
    fills: Dict[str, bool] = field(default_factory=dict)

    def add_tag_columns(self, tags: Dict[str, str]):
        for name, value in tags.items():
            column = self.columns.get(name)
            if column is None:
                column = Column(
                    field=Field(Name=name, Type=Field_Type_Tag),
                    col=ColVal(),
                )
                column.add_nulls(self.row_count)
            column.add_value(value)
            self.fills[name] = True
            self.columns[name] = column

    def add_field_columns(self, fields: Dict[str, Union[str, int, float, bool]]):
        for name, value in fields.items():
            column = self.columns.get(name)
            if column is None:
                column = Column(
                    field=Field(Name=name, Type=get_field_type(value)),
                    col=ColVal(),
                )
                column.add_nulls(self.row_count)
            column.add_value(value)
            self.fills[name] = True
            self.columns[name] = column

    def add_timestamp(self, timestamp):
        column = self.columns.get(TimeField)
        if column is None:
            column = Column(
                field=Field(Name=TimeField, Type=Field_Type_Int),
                col=ColVal(),
            )
            column.add_nulls(self.row_count)
        column.add_value(timestamp)
        self.columns[TimeField] = column

        self.min_time = min(self.min_time, timestamp)
        self.max_time = max(self.max_time, timestamp)

    def add_miss_value_columns(self):
        for name, ok in self.fills.items():
            if ok is True:
                continue
            column = self.columns[name]
            if column is None:
                continue
            count = self.row_count - column.col.Len
            if count <= 0:
                continue
            column.add_nulls(count)

        for name in self.fills:
            self.fills[name] = False

    def add_point(self, point: Point):
        self.add_tag_columns(point.tags)
        self.add_field_columns(point.fields)
        self.add_timestamp(point.generate_timestamp())
        self.row_count += 1
        self.add_miss_value_columns()

    def convert_to_record(self):
        if len(self.columns) == 0:
            raise err_empty_record
        tags_field = []
        tags_col = []
        fields_field = []
        fields_col = []
        timestamps_field = []
        timestamps_col = []
        for column in self.columns.values():
            if column.field.Name == TimeField:
                timestamps_field.append(column.field)
                timestamps_col.append(column.col)
                continue
            if column.field.Type == Field_Type_Tag:
                tags_field.append(column.field)
                tags_col.append(column.col)
                continue
            fields_field.append(column.field)
            fields_col.append(column.col)
        fields = fields_field + tags_field + timestamps_field
        cols = fields_col + tags_col + timestamps_col
        return Record(Fields=fields, ColVals=cols)
