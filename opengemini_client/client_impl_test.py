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
