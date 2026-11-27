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

from opengemini_client import client_impl
from opengemini_client import models


class TestClient(unittest.TestCase):

    def test_new_client_address_len(self):
        cfg = models.Config(address=[],
                            batch_config=models.BatchConfig(batch_size=10, batch_interval=10),
                            timeout=datetime.timedelta(seconds=30), connection_timeout=datetime.timedelta(seconds=10),
                            gzip_enabled=False, tls_enabled=False
                            )
        with self.assertRaises(ValueError):
            client_impl.OpenGeminiDBClient(cfg)

    def test_new_client_batch_size(self):
        cfg = models.Config(address=[models.Address(host='127.0.0.1', port=8080)],
                            batch_config=models.BatchConfig(batch_size=0, batch_interval=10),
                            timeout=datetime.timedelta(seconds=30), connection_timeout=datetime.timedelta(seconds=10),
                            gzip_enabled=False, tls_enabled=False
                            )
        with self.assertRaises(ValueError):
            client_impl.OpenGeminiDBClient(cfg)

    def test_new_client_batch_interval(self):
        cfg = models.Config(address=[models.Address(host='127.0.0.1', port=8080)],
                            batch_config=models.BatchConfig(batch_size=10, batch_interval=0),
                            timeout=datetime.timedelta(seconds=30), connection_timeout=datetime.timedelta(seconds=10),
                            gzip_enabled=False, tls_enabled=False
                            )
        with self.assertRaises(ValueError):
            client_impl.OpenGeminiDBClient(cfg)


class FakeResponse:
    def __init__(self, payload: dict):
        self.payload = payload

    def json(self) -> dict:
        return self.payload


class TestResolveQueryBody(unittest.TestCase):

    def test_resolve_query_body_with_series_tags(self):
        resp = FakeResponse({'results': [{'series': [{'name': 'cpu',
                                                     'tags': {'host': 'host-1', 'region': 'cn'},
                                                     'columns': ['time', 'value'],
                                                     'values': [[1, 12.0]]}]}]})
        query_result = client_impl.resolve_query_body(resp)
        self.assertEqual(query_result.error, None)
        self.assertEqual(len(query_result.results), 1)
        series = query_result.results[0].series
        self.assertEqual(len(series), 1)
        self.assertEqual(series[0].name, 'cpu')
        self.assertEqual(series[0].tags, {'host': 'host-1', 'region': 'cn'})
        self.assertEqual(series[0].columns, ['time', 'value'])
        self.assertEqual(series[0].values, [[1, 12.0]])

    def test_resolve_query_body_without_series_tags(self):
        resp = FakeResponse({'results': [{'series': [{'name': 'cpu',
                                                     'columns': ['time', 'value'],
                                                     'values': [[1, 12.0]]}]}]})
        query_result = client_impl.resolve_query_body(resp)
        series = query_result.results[0].series
        self.assertEqual(len(series), 1)
        self.assertEqual(series[0].tags, {})
