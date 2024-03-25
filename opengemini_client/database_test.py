import time
import unittest

from opengemini_client import client_impl
from opengemini_client import models
from opengemini_client import client_impl_test


class WriteTest(unittest.TestCase):

    def test_create_database(self):
        with client_impl.OpenGeminiDBClient(config=client_impl_test.common_test_config()) as cli:
            cli.create_database('create_db_test')
            res = cli.show_databases()
            self.assertEqual(True, 'create_db_test' in res)
            cli.drop_database('create_db_test')

    def test_create_database_with_rp(self):
        with client_impl.OpenGeminiDBClient(config=client_impl_test.common_test_config()) as cli:
            cli.create_database_with_rp('create_db_with_rp_test', models.RpConfig(name='db_with_rp_test',
                                                                                  duration='1h',
                                                                                  shard_group_duration='10m',
                                                                                  index_duration='10m'))
            qr = cli.query(models.Query(database='create_db_with_rp_test', command='SHOW RETENTION POLICIES',
                                        retention_policy=''))
            print(qr)
            res = cli.show_databases()
            self.assertEqual(True, 'create_db_with_rp_test' in res)
            cli.drop_database('create_db_with_rp_test')

    def test_drop_database(self):
        with client_impl.OpenGeminiDBClient(config=client_impl_test.common_test_config()) as cli:
            cli.create_database('drop_db_test')
            cli.drop_database('drop_db_test')
            time.sleep(3)
            res = cli.show_databases()
            self.assertEqual(False, 'drop_db_test' in res)
