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

from opengemini_client import models
from opengemini_client import test_utils


class RetentionPolicyTest(unittest.TestCase):

    def test_create_retention_policy_empty_db_parameter(self):
        dbname = inspect.currentframe().f_code.co_name
        rp_config = models.RpConfig(dbname, '2h', '2h', '2h')
        with test_utils.get_test_default_client() as cli:
            with self.assertRaises(ValueError):
                cli.create_retention_policy(dbname='', rp_config=rp_config, is_default=True)

    def test_create_retention_policy_success(self):
        dbname = inspect.currentframe().f_code.co_name
        rp_config = models.RpConfig(dbname, '2h', '2h', '2h')
        with test_utils.get_test_default_client() as cli:
            cli.create_database(dbname)
            qr = cli.create_retention_policy(dbname=dbname, rp_config=rp_config, is_default=True)
            self.assertEqual(qr.error, None)
            cli.drop_retention_policy(dbname=dbname, retention_policy=rp_config.name)
            cli.drop_database(dbname)

    def test_show_retention_policy_empty_db_parameter(self):
        with test_utils.get_test_default_client() as cli:
            with self.assertRaises(ValueError):
                cli.show_retention_policies('')

    def test_show_retention_policies_success(self):
        dbname = inspect.currentframe().f_code.co_name
        rp_config = models.RpConfig(dbname, '2h', '2h', '2h')
        with test_utils.get_test_default_client() as cli:
            cli.create_database(dbname)
            cli.create_retention_policy(dbname=dbname, rp_config=rp_config, is_default=True)
            retention_policies = cli.show_retention_policies(dbname=dbname)
            rp_config_name = [rp[0] for rp in retention_policies]
            self.assertTrue(rp_config.name in rp_config_name)
            cli.drop_retention_policy(dbname=dbname, retention_policy=rp_config.name)
            cli.drop_database(dbname)

    def test_drop_retention_policy_success(self):
        dbname = inspect.currentframe().f_code.co_name
        rp_config = models.RpConfig(dbname, '2h', '2h', '2h')
        with test_utils.get_test_default_client() as cli:
            cli.create_database(dbname)
            cli.create_retention_policy(dbname=dbname, rp_config=rp_config, is_default=True)
            qr = cli.drop_retention_policy(dbname=dbname, retention_policy=rp_config.name)
            self.assertEqual(qr.error, None)
            cli.drop_database(dbname)

    def test_drop_retention_policy_no_db_parameters(self):
        dbname = inspect.currentframe().f_code.co_name
        rp_config = models.RpConfig(dbname, '2h', '2h', '2h')
        with test_utils.get_test_default_client() as cli:
            cli.create_database(dbname)
            cli.create_retention_policy(dbname=dbname, rp_config=rp_config, is_default=True)
            with self.assertRaises(ValueError):
                cli.drop_retention_policy('', retention_policy=rp_config.name)
            cli.drop_retention_policy(dbname=dbname, retention_policy=rp_config.name)
            cli.drop_database(dbname)

    def test_drop_retention_policy_no_rp_parameters(self):
        dbname = inspect.currentframe().f_code.co_name
        rp_config = models.RpConfig(dbname, '2h', '2h', '2h')
        with test_utils.get_test_default_client() as cli:
            cli.create_database(dbname)
            cli.create_retention_policy(dbname=dbname, rp_config=rp_config, is_default=True)
            with self.assertRaises(ValueError):
                cli.drop_retention_policy(dbname, retention_policy='')
            cli.drop_retention_policy(dbname=dbname, retention_policy=rp_config.name)
            cli.drop_database(dbname)
