import datetime
import unittest

from opengemini_client import client_impl
from opengemini_client import models


class QueryTest(unittest.TestCase):

    def test_query_databases_success(self):
        cfg = models.Config(address=[models.Address(host='127.0.0.1', port=8086)],
                            auth_config=models.AuthConfig(auth_type=models.AuthType(0)),
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
            series = result.series
            self.assertEqual(len(series), 1)
