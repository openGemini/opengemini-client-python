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

import inspect
import unittest

from opengemini_client import test_utils


class DatabaseTest(unittest.TestCase):

    def test_create_databases_success(self):
        dbname = inspect.currentframe().f_code.co_name
        with test_utils.get_test_default_client() as cli:
            qr = cli.create_database(database=dbname)
            self.assertEqual(qr.error, None)
            qr = cli.drop_database(database=dbname)
            self.assertEqual(qr.error, None)

    def test_show_databases_success(self):
        dbname = inspect.currentframe().f_code.co_name
        with test_utils.get_test_default_client() as cli:
            qr = cli.create_database(database=dbname)
            self.assertEqual(qr.error, None)
            new_db_list = cli.show_databases()
            self.assertTrue(dbname in new_db_list)
            qr = cli.drop_database(database=dbname)
            self.assertEqual(qr.error, None)

    def test_create_databases_with_empty_db(self):
        with test_utils.get_test_default_client() as cli:
            with self.assertRaises(ValueError):
                cli.create_database(database='')

    def test_drop_databases_success(self):
        dbname = inspect.currentframe().f_code.co_name
        with test_utils.get_test_default_client() as cli:
            qr = cli.create_database(database=dbname)
            self.assertEqual(qr.error, None)
            qr = cli.drop_database(database=dbname)
            self.assertEqual(qr.error, None)

    def test_drop_databases_with_empty_db(self):
        with test_utils.get_test_default_client() as cli:
            with self.assertRaises(ValueError):
                cli.drop_database(database='')
