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

import datetime
import time
import unittest

from opengemini_client import client_impl, test_utils
from opengemini_client import models


class QueryTest(unittest.TestCase):

    def test_query_no_db_in_opengemini(self):
        cfg = models.Config(address=[models.Address(host='127.0.0.1', port=8086)],
                            batch_config=models.BatchConfig(batch_size=10, batch_interval=10),
                            timeout=datetime.timedelta(seconds=30), connection_timeout=datetime.timedelta(seconds=10),
                            gzip_enabled=False, tls_enabled=False
                            )
        with client_impl.OpenGeminiDBClient(cfg) as cli:
            qr = cli.query(query=models.Query('', 'show databases', ''))
            self.assertEqual(qr.error, None)
            results = qr.results
            self.assertEqual(len(results), 1)
            result = results[0]
            self.assertEqual(result.error, None)

    def test_query_show_with_result_any(self):
        with test_utils.get_test_default_client() as cli:
            cli.create_database('show_test')
            point = models.Point(measurement='show_mm', precision=models.Precision.PrecisionSecond,
                                 fields={'x': 12.0, 'y': 4.0}, tags={'location': 'xy'},
                                 timestamp=datetime.datetime.now())
            cli.write_batch_points("show_test", models.BatchPoints(points=[point]))
            time.sleep(3)
            values_results = cli.show_tag_keys('show_test', 'show tag keys from show_mm')
            print(values_results)
            self.assertEqual(len(values_results), 1)
            self.assertEqual(values_results[0].measurement, 'show_mm')

            values_results = cli.show_tag_keys('show_test', 'show series from show_mm')
            print(values_results)
            self.assertEqual(len(values_results), 1)
            self.assertEqual(len(values_results[0].values), 1)
            self.assertRegex(values_results[0].values[0], 'show_mm')
            cli.drop_database('show_test')

    def test_query_show_with_result_key_value(self):
        with test_utils.get_test_default_client() as cli:
            cli.create_database('show_test1')
            point1 = models.Point(measurement='show_mm', precision=models.Precision.PrecisionSecond,
                                  fields={'x': 12.0, 'y': 4.0}, tags={'location': 'sz'},
                                  timestamp=datetime.datetime.now())
            point2 = models.Point(measurement='show_mm', precision=models.Precision.PrecisionSecond,
                                  fields={'x': 12.0, 'y': 4.0}, tags={'location': 'gz'},
                                  timestamp=datetime.datetime.now())
            cli.write_batch_points("show_test1", models.BatchPoints(points=[point1, point2]))
            time.sleep(3)
            values_results = cli.show_tag_values('show_test1', 'show tag values from show_mm with key=location')
            print(values_results)
            self.assertEqual(len(values_results), 1)
            self.assertEqual(len(values_results[0].values), 2)
            self.assertEqual(values_results[0].measurement, 'show_mm')

            values_results = cli.show_field_keys('show_test1', 'show field keys from show_mm')
            print(values_results)
            self.assertEqual(len(values_results), 1)
            self.assertEqual(len(values_results[0].values), 2)
            self.assertEqual(values_results[0].measurement, 'show_mm')
            cli.drop_database('show_test1')
