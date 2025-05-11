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

import time
import unittest
from datetime import datetime

from opengemini_client import models
from opengemini_client import test_utils


class GrpcClientTest(unittest.TestCase):

    def test_write_success(self):
        with test_utils.get_test_default_client() as cli:
            cli.create_database('grpc_write_test')
            point1 = models.Point(
                measurement='write_mm',
                precision=models.Precision.PrecisionSecond,
                fields={'x': 12.0, 'y': 4.0},
                tags={'a': 'ax', 'b': 'bx'},
                timestamp=datetime.now(),
            )
            point2 = models.Point(
                measurement='write_mm',
                precision=models.Precision.PrecisionSecond,
                fields={'x': 15.0, 'y': 5.0, 'z': 8, 'name': 'xx'},
                tags={'a': 'ax', 'b': 'bx', 'c': 'cz'},
                timestamp=datetime.now(),
            )
            point3 = models.Point(
                measurement='write_nn',
                precision=models.Precision.PrecisionSecond,
                fields={'name': 'xx', 'age': 20},
                tags={'sex': 'man'},
                timestamp=datetime.now(),
            )
            cli.write_by_grpc("grpc_write_test", models.BatchPoints(points=[point1, point2, point3]))
            time.sleep(5)
            qr = cli.query(models.Query(database='grpc_write_test', command='select * from write_mm',
                                        retention_policy=''))
            print(qr)
            self.assertNotEqual(len(qr.results), 0)
            cli.drop_database('grpc_write_test')
