import inspect
import unittest

from opengemini_client import test_utils


class DatabaseTest(unittest.TestCase):

    def test_create_databases_success(self):
        dbname = inspect.currentframe().f_code.co_name
        cli = test_utils.get_test_default_client()
        qr = cli.create_database(database=dbname)
        self.assertEqual(qr.error, None)
        qr = cli.drop_database(database=dbname)
        self.assertEqual(qr.error, None)
        cli.close()

    def test_show_databases_success(self):
        dbname = inspect.currentframe().f_code.co_name
        cli = test_utils.get_test_default_client()
        qr = cli.create_database(database=dbname)
        self.assertEqual(qr.error, None)
        new_db_list = cli.show_databases()
        self.assertTrue(dbname in new_db_list)
        qr = cli.drop_database(database=dbname)
        self.assertEqual(qr.error, None)
        cli.close()

    def test_create_databases_with_empty_db(self):
        cli = test_utils.get_test_default_client()
        with self.assertRaises(ValueError):
            cli.create_database(database='')
        cli.close()

    def test_drop_databases_success(self):
        dbname = inspect.currentframe().f_code.co_name
        cli = test_utils.get_test_default_client()
        qr = cli.create_database(database=dbname)
        self.assertEqual(qr.error, None)
        qr = cli.drop_database(database=dbname)
        self.assertEqual(qr.error, None)
        cli.close()

    def test_drop_databases_with_empty_db(self):
        cli = test_utils.get_test_default_client()
        with self.assertRaises(ValueError):
            cli.drop_database(database='')
        cli.close()
