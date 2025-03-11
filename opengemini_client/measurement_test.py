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

import unittest
import time

from opengemini_client import test_utils
from opengemini_client.measurement import Measurement, FieldType, IndexType, ErrEmptyTagOrField, ErrEmptyDatabaseName, \
    ErrEmptyMeasurement, ErrEmptyIndexList, MeasurementCondition, ComparisonOperator


class MeasurementTest(unittest.TestCase):

    def test_create_measurement_success(self):
        with test_utils.get_test_default_client() as cli:
            cli.create_database('m_test')
            cli.create_measurement(measurement=Measurement(
                database="m_test",
                measurement="m1",
                retention_policy="",
                tags=["tag1", "tag2"],
                fields={
                    "field_str": FieldType.FieldTypeString,
                    "field_int64": FieldType.FieldTypeInt64,
                },
                index_type=IndexType.IndexTypeText,
                index_list=["field_str"]
            ))
            time.sleep(5)
            field_results = cli.show_field_keys('m_test', 'show field keys from m1')
            print(field_results)
            self.assertEqual(2, len(field_results[0].values))
            cli.drop_database("m_test")

    def test_create_measurement_failed(self):
        with test_utils.get_test_default_client() as cli:
            # measurement is None
            with self.assertRaises(ValueError) as context:
                cli.create_measurement(measurement=None)
            print(context.exception)
            self.assertRegex(str(context.exception), "empty measurement")

            # database is None
            with self.assertRaises(ValueError) as context:
                cli.create_measurement(measurement=Measurement(
                    database="",
                    measurement="m1",
                    retention_policy="",
                ))
            print(context.exception)
            self.assertRegex(str(context.exception), ErrEmptyDatabaseName)

            # measurement is None
            with self.assertRaises(ValueError) as context:
                cli.create_measurement(measurement=Measurement(
                    database="m_test",
                    measurement="",
                    retention_policy="",
                ))
            print(context.exception)
            self.assertRegex(str(context.exception), ErrEmptyMeasurement)

            # tags fields is None
            with self.assertRaises(ValueError) as context:
                cli.create_measurement(measurement=Measurement(
                    database="m_test",
                    measurement="m1",
                    retention_policy="",
                ))
            print(context.exception)
            self.assertRegex(str(context.exception), ErrEmptyTagOrField)

            with self.assertRaises(ValueError) as context:
                cli.create_measurement(measurement=Measurement(
                    database="m_test",
                    measurement="m1",
                    retention_policy="",
                    tags=["tag1", "tag2"],
                    fields={
                        "field_str": FieldType.FieldTypeString,
                        "field_int64": FieldType.FieldTypeInt64,
                    },
                    index_type=IndexType.IndexTypeText,
                ))
            print(context.exception)
            self.assertRegex(str(context.exception), ErrEmptyIndexList)

    def test_show_measurements_success(self):
        with test_utils.get_test_default_client() as cli:
            cli.create_database('m_show_test')
            cli.create_measurement(measurement=Measurement(
                database="m_show_test",
                measurement="m1",
                retention_policy="",
                tags=["tag1"],
                fields={
                    "field_str": FieldType.FieldTypeString,
                },
                index_type=IndexType.IndexTypeText,
                index_list=["field_str"]
            ))
            cli.create_measurement(measurement=Measurement(
                database="m_show_test",
                measurement="m2",
                retention_policy="",
                tags=["tag2"],
                fields={
                    "field_str": FieldType.FieldTypeString,
                },
                index_type=IndexType.IndexTypeText,
                index_list=["field_str"]
            ))
            time.sleep(5)
            ms = cli.show_measurements(condition=MeasurementCondition(
                database="m_show_test",
                Operator=ComparisonOperator.Match,
                Value="/m/"
            ))
            print(ms)
            self.assertEqual(2, len(ms))
            cli.drop_database("m_show_test")

    def test_drop_measurement_success(self):
        with test_utils.get_test_default_client() as cli:
            cli.create_database('m_test')
            cli.create_measurement(measurement=Measurement(
                database="m_test",
                measurement="m1",
                retention_policy="",
                tags=["tag1"],
                fields={
                    "field_str": FieldType.FieldTypeString,
                },
                index_type=IndexType.IndexTypeText,
                index_list=["field_str"]
            ))
            cli.drop_measurement("m_test", "", "m1")
            ms = cli.show_measurements(condition=MeasurementCondition(
                database="m_test",
                Operator=ComparisonOperator.Match,
                Value="/m/"
            ))
            print(ms)
            self.assertEqual(0, len(ms))
            cli.drop_database("m_test")
