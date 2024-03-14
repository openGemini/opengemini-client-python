import datetime
import unittest
from opengemini_client import client_impl
from opengemini_client import models


class TestClient(unittest.TestCase):

    def test_query_error(self):
        cfg = models.Config(address=[models.Address(host='127.0.0.1', port=8081)],
                            auth_config=models.AuthConfig(auth_type=models.AuthType(0)),
                            batch_config=models.BatchConfig(batch_size=10, batch_interval=10),
                            timeout=datetime.timedelta(seconds=30), connection_timeout=datetime.timedelta(seconds=10),
                            gzip_enabled=False, tls_enabled=False
                            )
        cli = client_impl.OpenGeminiDBClient(cfg)
        _, error = cli.query(query=models.Query('abc', 'SELECT * INTO "newmeas" FROM "MYMEAS"', ''))
        print(error.content)
        self.assertRegex(str(error.content), "openGeminiDB server error")
        cli.close()

    def test_query_success(self):
        cfg = models.Config(address=[models.Address(host='127.0.0.1', port=8086)],
                            auth_config=models.AuthConfig(auth_type=models.AuthType(0)),
                            batch_config=models.BatchConfig(batch_size=10, batch_interval=10),
                            timeout=datetime.timedelta(seconds=30), connection_timeout=datetime.timedelta(seconds=10),
                            gzip_enabled=False, tls_enabled=False
                            )
        cli = client_impl.OpenGeminiDBClient(cfg)
        qr, _ = cli.query(query=models.Query('', 'create database test_openGeminiDB_1', ''))
        print(qr)
        self.assertEqual(qr.results['results'], [{'statement_id': 0}])
        qr, _ = cli.query(query=models.Query('', 'show databases', ''))
        result = qr.results['results'][0]
        self.assertTrue(['test_openGeminiDB_1'] in result["series"][0]['values'])
        cli.close()
