import base64
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


class OpenGeminiDBClient(Client, ABC):
    config: Config
    session: requests.Session
    endpoints: List[str]
    prevIdx: AtomicInt

    def __init__(self, config: Config):
        self.config = config
        self.session = requests.Session()
        protocol = "https://" if config.tls_enabled else "http://"
        self.endpoints = [f"{protocol}{addr.host}:{addr.port}" for addr in config.address]
        self.prevIdx = AtomicInt(-1)
        self._set_default_headers()

    def _set_default_headers(self):
        headers = {'Content-Type': 'application/json'}
        if self.config.auth_config and self.config.auth_config.auth_type == self.config.auth_config.auth_type.PASSWORD:
            encode_string = f"{self.config.auth_config.username}:{self.config.auth_config.password}"
            authorization = "Basic " + base64.b64encode(encode_string.encode()).decode()
            headers["Authorization"] = authorization

        if self.config.gzip_enabled:
            headers.update({"Content-Encoding": "gzip", "Accept-Encoding": "gzip"})

        self.session.headers.update(headers)

    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        self.session.close()

    def request(self, method, server_url, url_path, headers=None, body=None) -> (requests.Response, Error):
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
