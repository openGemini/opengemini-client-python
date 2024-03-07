import base64
import gzip
import io
from abc import ABC
from http import HTTPStatus
from typing import List

import requests

from opengemini_client.client import Client
from opengemini_client.exceptions import Error
from opengemini_client.models import Config, BatchPoints
from opengemini_client.url_const import UrlConst


class RequestDetails:
    def __init__(self, query_values: dict, headers: dict, body: bytes):
        self.query_values = query_values
        self.headers = headers
        self.body = body


def close():
    requests.Session().close()


class OpenGeminiDBClient(Client, ABC):
    endpoints: List[str]

    def __init__(self, config: Config):
        self.config = config
        protocol = "https://" if config.tls_enabled else "http://"
        self.endpoints = [f"{protocol}{addr.host}:{addr.port}" for addr in config.address]

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        close()

    def update_headers(self, method, url_path, headers=None) -> dict:
        if not self.config.auth_config:
            return headers

        if headers is None:
            headers = {}

        headers.setdefault('Content-Type', 'application/json')

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

    def request(self, method, server_url, url_path, details: RequestDetails):
        details.headers = self.update_headers(method, url_path, details.headers)
        full_url = server_url + url_path
        data = details.body
        if self.config.gzip_enabled:
            if data is not None:
                compressed = io.BytesIO()
                with gzip.GzipFile(
                        compresslevel=9,
                        fileobj=compressed,
                        mode='w'
                ) as f:
                    f.write(details.body)
                    data = compressed.getvalue()

        req = requests.Request(method, full_url, data=data, headers=details.headers)
        prepared = req.prepare()
        try:
            resp = requests.Session().send(prepared)
            if 500 <= resp.status_code < 600:
                return Error("openGeminiDB server error"), None
            return None, resp
        except requests.exceptions.RequestException as e:
            return Error(f"openGeminiDB server error {e}"), None

    def exec_http_request_by_index(self, idx, method, url_path, details: RequestDetails):
        if idx >= len(self.endpoints) or idx < 0:
            return Error("openGeminiDB client error.Index out of range"), None
        return self.request(method, self.endpoints[idx], url_path, details)

    def ping(self, idx: int):
        error, resp = self.exec_http_request_by_index(idx, 'GET', UrlConst.PING, RequestDetails({}, {}, b''))
        if error is not None:
            return error
        if resp.status_code == HTTPStatus.OK:
            return None
        return Error(f"ping openGeminiDB status is {resp.status_code}")

    def query(self, query: object) -> tuple:
        return ()

    def write_batch_points(self, database: str, batch_points: BatchPoints) -> Error:
        return Error("")
