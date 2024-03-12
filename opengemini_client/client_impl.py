import base64
import datetime
import gzip
import io
from abc import ABC
from http import HTTPStatus
from typing import List

import requests

from opengemini_client.client import Client
from opengemini_client.exceptions import Error
from opengemini_client.models import Config, BatchPoints, Query
from opengemini_client.url_const import UrlConst
from opengemini_client.utils import AtomicInt


def check_conifg(config: Config):
    if len(config.address) == 0:
        raise ValueError("must have at least on address")

    if config.auth_config is not None:
        if config.auth_config.auth_type.PASSWORD == 0:
            if len(config.auth_config.username) == 0:
                raise ValueError("invalid auth config due to empty username")
            if len(config.auth_config.password) == 0:
                raise ValueError("invalid auth config due to empty password")
        if config.auth_config.auth_type.TOKEN == 1 and len(config.auth_config.token) == 0:
            raise ValueError("invalid auth config due to empty token")

    if config.batch_config is not None:
        if config.batch_config.batch_interval <= 0:
            raise ValueError("batch enabled,batch interval must be greater than 0")
        if config.batch_config.batch_size <= 0:
            raise ValueError("batch enabled,batch size must be greater than 0")

    if config.timeout <= datetime.timedelta(seconds=0):
        config.timeout = datetime.timedelta(seconds=30)

    if config.connection_timeout <= datetime.timedelta(seconds=0):
        config.connection_timeout = datetime.timedelta(seconds=10)

    return config


class OpenGeminiDBClient(Client, ABC):
    config: Config
    session: requests.Session
    endpoints: List[str]
    pre_idx: AtomicInt

    def __init__(self, config: Config):
        self.config = check_conifg(config)
        self.session = requests.Session()
        protocol = "https://" if config.tls_enabled else "http://"
        self.endpoints = [f"{protocol}{addr.host}:{addr.port}" for addr in config.address]
        self.pre_idx = AtomicInt(-1)

    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        self.session.close()

    def get_server_url(self):
        self.pre_idx.increment()
        idx = int(self.pre_idx.get_value()) % len(self.endpoints)
        return self.endpoints[idx]

    def update_headers(self, method, url_path, headers=None) -> dict:
        if not self.config.auth_config:
            return headers

        if headers is None:
            headers = {}

        headers.setdefault('Content-Type', 'application/json')

        if not self.config.auth_config:
            return headers

        if url_path in UrlConst.no_auth_required:
            if method in UrlConst.no_auth_required[url_path]:
                return headers

        if self.config.auth_config.auth_type == self.config.auth_config.auth_type.PASSWORD:
            encode_string = f"{self.config.auth_config.username}:{self.config.auth_config.password}"
            authorization = "Basic " + base64.b64encode(encode_string.encode()).decode()
            headers["Authorization"] = authorization

        if self.config.gzip_enabled:
            headers.update({"Content-Encoding": "gzip", "Accept-Encoding": "gzip"})

        return headers

    def request(self, method, server_url, url_path, headers=None, body=None) -> (requests.Response, Error):
        headers = self.update_headers(method, url_path, headers)
        full_url = server_url + url_path
        if self.config.gzip_enabled and body is not None:
            compressed = io.BytesIO()
            with gzip.GzipFile(compresslevel=9, fileobj=compressed, mode='w') as f:
                f.write(body)
                body = compressed.getvalue()

        req = requests.Request(method, full_url, data=body, headers=headers)
        prepared = req.prepare()
        try:
            resp = self.session.send(prepared)
            if 500 <= resp.status_code < 600:
                return None, Error("openGeminiDB server error")
            return resp, None
        except requests.exceptions.RequestException as e:
            return None, Error(f"openGeminiDB server error {e}")

    def exec_http_request_by_index(self, idx, method, url_path, headers=None, body=None) -> (requests.Response, Error):
        if idx >= len(self.endpoints) or idx < 0:
            return Error("openGeminiDB client error.Index out of range"), None
        return self.request(method, self.endpoints[idx], url_path, headers, body)

    def ping(self, idx: int):
        resp, error = self.exec_http_request_by_index(idx, 'GET', UrlConst.PING)
        if error is not None:
            return error
        if resp.status_code == HTTPStatus.NO_CONTENT:
            return None
        return Error(f"ping openGeminiDB status is {resp.status_code}")

    def query(self, query: Query) -> tuple:
        return ()

    def write_batch_points(self, database: str, batch_points: BatchPoints) -> Error:
        return Error("")
