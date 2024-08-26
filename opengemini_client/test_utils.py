from opengemini_client import client_impl
from opengemini_client import models


def get_test_default_client():
    cfg = models.Config(address=[models.Address(host='127.0.0.1', port=8086)])
    cli = client_impl.OpenGeminiDBClient(cfg)
    return cli
