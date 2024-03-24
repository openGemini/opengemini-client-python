import unittest
from datetime import datetime, timedelta

import requests

from opengemini_client import client_impl
from opengemini_client import models


class WriteTest(unittest.TestCase):

    def test_write_batch_points_success(self):
        cfg = models.Config(address=[models.Address(host='127.0.0.1', port=8086)],
                            auth_config=models.AuthConfig(auth_type=models.AuthType(0)),
                            batch_config=models.BatchConfig(batch_size=10, batch_interval=10),
                            timeout=timedelta(seconds=10), connection_timeout=timedelta(seconds=10),
                            gzip_enabled=False, tls_enabled=False
                            )
        with client_impl.OpenGeminiDBClient(config=cfg) as cli:
            cli.create_database('write_test')
            point = models.Point(measurement='write_mm', precision=models.PrecisionType.PrecisionSecond,
                                 fields={'x': 12.0, 'y': 4.0}, tags={'a': 'ax', 'b': 'bx'}, timestamp=datetime.now())
            cli.write_batch_points("write_test", models.BatchPoints(points=[point]))

    def test_write_batch_points_fail_with_no_database(self):
        cfg = models.Config(address=[models.Address(host='127.0.0.1', port=8086)],
                            auth_config=models.AuthConfig(auth_type=models.AuthType(0)),
                            batch_config=models.BatchConfig(batch_size=10, batch_interval=10),
                            timeout=timedelta(seconds=10), connection_timeout=timedelta(seconds=10),
                            gzip_enabled=False, tls_enabled=False
                            )
        with client_impl.OpenGeminiDBClient(config=cfg) as cli:
            point = models.Point(measurement='write_mm', precision=models.PrecisionType.PrecisionSecond,
                                 fields={'x': 6.0, 'y': 4.0}, timestamp=datetime.now())
            with self.assertRaises(requests.exceptions.HTTPError) as context:
                cli.write_batch_points("write_test1", models.BatchPoints(points=[point]))
            self.assertRegex(str(context.exception), "database not found")


