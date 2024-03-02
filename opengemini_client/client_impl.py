import base64
import datetime
import json
import threading
from http import HTTPStatus

import requests

from opengemini_client.common import Address
from opengemini_client.common import AuthType
from opengemini_client.common import Config
from opengemini_client.query import Query
from opengemini_client.query_result import QueryResult
from opengemini_client.url_const import UrlConst


class AtomicInt32:
    def __init__(self, value=0):
        self._value = value
        self._lock = threading.Lock()

    def increment(self):
        with self._lock:
            self._value += 1

    def get_value(self):
        with self._lock:
            return self._value


class Endpoint:
    def __init__(self, url):
        self.url = url


class RequestDetails:
    def __init__(self, query_values=None, headers=None, body=None):
        self.query_values = query_values if query_values is not None else {}
        self.headers = headers if headers is not None else {}
        self.body = body


class Client:
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
        self.prev_idx = AtomicInt32(5)
        self.data_chan = {}

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
        server_len = len(self.endpoints)
        for i in range(server_len, 0, -1):
            idx = (self.prev_idx + 1) % server_len
            return self.endpoints[idx].url

    def ping(self, idx):
        resp = self.execute_http_get_by_idx(idx, UrlConst.URL_PING, None)
        if resp.status_code != HTTPStatus.NO_CONTENT:
            return None

        return None

    def query(self, query: Query):
        query_value = {
            "db": query.database,
            "q": query.command,
            "rp": query.retention_policy
        }
        req = RequestDetails(query_value)
        resp = self.execute_http_get(UrlConst.URL_QUERY, req)
        resp.raise_for_status()
        qr = QueryResult(results=[], error='')
        qr.__dict__ = json.loads(resp.text)
        return qr


def _new_client(config: Config) -> Client:
    """
    creates a new client
    :param config: config object
    :return: Client object
    """
    if len(config.address) == 0:
        raise ValueError("must have at least one address")

    if config.auth_config is not None:
        if config.auth_config.auth_type == AuthType.AUTH_TYPE_TOKE \
                and len(config.auth_config.token) == 0:
            raise ValueError("invalid auth config due to empty token")
        if config.auth_config.auth_type == AuthType.AUTH_TYPE_PASSWORD:
            if len(config.auth_config.username) == 0:
                raise ValueError("invalid auth config due to empty username")

            if len(config.auth_config.password) == 0:
                raise ValueError("invalid auth config due to empty password")

    if config.batch_config is not None:
        if config.batch_config.batch_interval <= 0:
            raise ValueError("batch enabled, batch interval must be greater than 0")
        if config.batch_config.batch_size <= 0:
            raise ValueError("batch enabled, batch size must be greater than 0")

    if config.timeout <= 0:
        config.timeout = 30 * datetime.timedelta(seconds=1)

    if config.connection_timeout <= 0:
        config.connection_timeout = 10 * datetime.timedelta(seconds=1)

    endpoints = build_endpoints(config.address, config.tls_enabled)
    client = Client(config, endpoints)
    client.prev_idx.increment()
    return client


def build_endpoints(address: list[Address], tls_enabled: bool) -> list:
    urls = []
    protocol = "http://"
    if tls_enabled:
        protocol = "https://"
    for addr in address:
        url = protocol + addr.host + ":" + str(addr.port)
        urls.append(url)

    return urls


def new_client(config: Config) -> Client:
    return _new_client(config)
