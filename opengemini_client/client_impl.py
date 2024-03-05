import base64
from abc import ABC
from http import HTTPStatus

import requests

from opengemini_client.client import Client
from opengemini_client.models import Config, Endpoint, RequestDetails
from opengemini_client.url_const import UrlConst
from opengemini_client.utils import AtomicInt


class ClientImpl(Client, ABC):
    """
    OpenGemini client class
    """

    def __init__(self, config: Config, endpoints: list[Endpoint]):
        """
        OpenGemini client
        :param config:  config object
        :param endpoints:  urls
        """
        self.config = config
        self.endpoints = endpoints
        self.prev_idx = AtomicInt(5)
        self.data_chan = {}

    def ping(self, idx):
        resp = self.execute_http_get_by_idx(idx, UrlConst.PING, RequestDetails('', {}, any))
        if resp.status_code != HTTPStatus.NO_CONTENT:
            return None

        return None

    def update_auth_header(self, method, url_path, header=None):
        if not self.config.auth_config:
            return header

        if url_path in UrlConst.no_auth_required:
            if method in UrlConst.no_auth_required[url_path]:
                return header

        if header is None:
            header = {}

        if self.config.auth_config.auth_type == 0:
            encode_string = f"{self.config.auth_config.username}:{self.config.auth_config.password}"
            authorization = "Basic " + base64.b64encode(encode_string.encode()).decode()
            header["Authorization"] = authorization

        return header

    def execute_http_get_by_idx(self, idx, url_path, details: RequestDetails):
        return self.execute_http_request_by_idx(idx, "GET", url_path, details)

    def execute_http_request_by_idx(self, idx, method, url_path, details: RequestDetails):
        if idx >= len(self.endpoints) or idx < 0:
            raise ValueError("Index out of range")

        return self.execute_http_request_inner(method, self.endpoints[idx].url, url_path, details)

    def execute_http_get(self, url_path, details: RequestDetails):
        return self.execute_http_request("GET", url_path, details)

    def execute_http_post(self, url_path, details: RequestDetails):
        return self.execute_http_request("POST", url_path, details)

    def execute_http_request_inner(self, method, server_url, url_path, details: RequestDetails):
        details.headers = self.update_auth_header(method, url_path, details.headers)
        full_url = server_url + url_path
        req = requests.Request(method, full_url, data=details.body, headers=details.headers)
        prepared = req.prepare()
        return requests.Session().send(prepared)

    def execute_http_request(self, method, url_path, details: RequestDetails):
        server_url = self.get_server_url()
        return self.execute_http_request_inner(method, server_url, url_path, details)

    def get_server_url(self):
        server_url = []
        server_len = len(self.endpoints)
        if server_len <= 0:
            raise ValueError("endpoints is empty")

        for ep in self.endpoints:
            if ep is None:
                raise ValueError(f"{ep} is empty")
            server_url.append(ep.url)

        return server_url
