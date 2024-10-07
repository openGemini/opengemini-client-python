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
import unittest

import requests

from opengemini_client import client_impl, test_utils
from opengemini_client import models


class PingTest(unittest.TestCase):

    # noinspection PyMethodMayBeStatic
    def test_ping_success(self):
        with test_utils.get_test_default_client() as cli:
            cli.ping(0)

    def test_ping_error(self):
        cfg = models.Config(address=[models.Address(host='127.0.0.1', port=8080)],
                            batch_config=models.BatchConfig(batch_size=10, batch_interval=10),
                            timeout=datetime.timedelta(seconds=10), connection_timeout=datetime.timedelta(seconds=10),
                            gzip_enabled=False, tls_enabled=False
                            )
        with client_impl.OpenGeminiDBClient(config=cfg) as cli:
            with self.assertRaises(requests.exceptions.ConnectionError) as context:
                cli.ping(0)
            self.assertRegex(str(context.exception), "Connection refused")
