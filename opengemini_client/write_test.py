import time
import unittest
from datetime import datetime

import requests
from opengemini_client import models
from opengemini_client import test_utils


class WriteTest(unittest.TestCase):

    def test_write_batch_points_success(self):
        with test_utils.get_test_default_client() as cli:
            cli.create_database('write_test')
            point = models.Point(measurement='write_mm', precision=models.Precision.PrecisionSecond,
                                 fields={'x': 12.0, 'y': 4.0}, tags={'a': 'ax', 'b': 'bx'}, timestamp=datetime.now())
            cli.write_batch_points("write_test", models.BatchPoints(points=[point]))
            time.sleep(3)
            qr = cli.query(models.Query(database='write_test', command='select * from write_mm', retention_policy=''))
            print(qr)
            self.assertNotEqual(len(qr.results), 0)
            result = qr.results[0]
            series = result.series
            self.assertNotEqual(len(series), 0)
            cli.drop_database('write_test')

    def test_write_batch_points_fail_with_no_database(self):
        with test_utils.get_test_default_client() as cli:
            point = models.Point(measurement='write_mm', precision=models.Precision.PrecisionSecond,
                                 fields={'x': 6.0, 'y': 4.0}, timestamp=datetime.now())
            with self.assertRaises(requests.exceptions.HTTPError) as context:
                cli.write_batch_points("write_test1", models.BatchPoints(points=[point]))
            self.assertRegex(str(context.exception), "database not found")
