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

from opengemini_client import client_impl
from opengemini_client import models


def get_test_default_client():
    cfg = models.Config(address=[models.Address(host='127.0.0.1', port=8086)])
    cli = client_impl.OpenGeminiDBClient(cfg)
    return cli
