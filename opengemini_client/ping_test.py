import unittest
import datetime
from opengemini_client import client_impl
from opengemini_client import models


class TestClient(unittest.TestCase):

    def test_ping(self):
        cfg = models.Config(address=[models.Address(host='127.0.0.1', port=8080)],
                            auth_config=models.AuthConfig(auth_type=models.AuthType(0)),
                            batch_config=models.BatchConfig(batch_size=10, batch_interval=10),
                            timeout=datetime.timedelta(seconds=10), connection_timeout=datetime.timedelta(seconds=10),
                            gzip_enabled=False, tls_enabled=False
                            )

        cli = client_impl.OpenGeminiDBClient(config=cfg)
        error = cli.ping(0)
        self.assertNotEqual(error, None)
        self.assertRegex(error.content, "openGeminiDB server error")
