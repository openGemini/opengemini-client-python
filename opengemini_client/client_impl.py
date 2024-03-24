import base64
import datetime
import gzip
import io
from abc import ABC
from http import HTTPStatus
from typing import List

import requests
from requests import HTTPError

from opengemini_client.client import Client
from opengemini_client.models import Config, BatchPoints, Query, QueryResult, Series, SeriesResult, RpConfig
from opengemini_client.url_const import UrlConst
from opengemini_client.utils import AtomicInt


def check_config(config: Config):
    if len(config.address) == 0:
        raise ValueError("must have at least one address")

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


def convert_to_query_result(json_data):
    results = []
    for result in json_data.get('results', []):
        series_list: List[Series] = [
            Series(name=series.get('name', ''), columns=series['columns'], values=series['values'])
            for series in result.get('series', [])
            if series.get('values', [])
        ]
        series_result = SeriesResult(series=series_list, error=result.get('error'))
        results.append(series_result)

    return QueryResult(results=results, error=json_data.get('error'))


def resolve_query_body(resp: requests.Response):
    json_data = resp.json()
    qr = convert_to_query_result(json_data)
    err = qr.get_error()
    if len(err) > 0:
        raise HTTPError(f"query result has error: {err}")
    return qr


class OpenGeminiDBClient(Client, ABC):
    config: Config
    session: requests.Session
    endpoints: List[str]
    pre_idx: AtomicInt

    def __init__(self, config: Config):
        self.config = check_config(config)
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
        if headers is None:
            headers = {}

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

    def request(self, method, server_url, url_path, headers=None, body=None, params=None) -> requests.Response:
        if params is None:
            params = {}
        headers = self.update_headers(method, url_path, headers)
        full_url = server_url + url_path
        if self.config.gzip_enabled and body is not None:
            compressed = io.BytesIO()
            with gzip.GzipFile(compresslevel=9, fileobj=compressed, mode='w') as f:
                f.write(body)
                body = compressed.getvalue()

        req = requests.Request(method, full_url, data=body, headers=headers, params=params)
        prepared = req.prepare()
        resp = self.session.send(prepared)
        if not 200 <= resp.status_code < 300:
            raise HTTPError(f"HTTP error: {resp.status_code}, Response: {resp.text}")
        return resp

    def exec_http_request_by_index(self, idx, method, url_path, headers=None, body=None) -> requests.Response:
        if idx >= len(self.endpoints) or idx < 0:
            raise ValueError("openGeminiDB client error. Index out of range")
        return self.request(method, self.endpoints[idx], url_path, headers, body)

    def ping(self, idx: int):
        resp = self.exec_http_request_by_index(idx, 'GET', UrlConst.PING)
        if resp.status_code != HTTPStatus.NO_CONTENT:
            raise HTTPError(f"ping openGeminiDB status is {resp.status_code}")

    def query(self, query: Query) -> QueryResult:
        server_url = self.get_server_url()
        params = {'db': query.database, 'q': query.command, 'rp': query.retention_policy}

        resp = self.request(method='GET', server_url=server_url, url_path=UrlConst.QUERY, params=params)
        if resp.status_code == HTTPStatus.OK:
            return resolve_query_body(resp)
        raise HTTPError(f"Query error: {resp.status_code}, Response: {resp.text}")

    def write_batch_points(self, database: str, batch_points: BatchPoints):
        server_url = self.get_server_url()
        params = {'db': database}
        writer = io.StringIO()
        for bp in batch_points.points:
            if bp is None:
                continue
            writer.write(bp.to_string())
            writer.write('\n')
        body = writer.getvalue().encode()
        writer.close()
        resp = self.request(method="POST", server_url=server_url, url_path=UrlConst.WRITE, params=params, body=body)
        if resp.status_code != HTTPStatus.NO_CONTENT:
            raise HTTPError(f"write error: {resp.status_code}, Response: {resp.text}")

    def create_database(self, database: str):
        server_url = self.get_server_url()
        params = {'q': 'create database ' + database}

        resp = self.request(method='POST', server_url=server_url, url_path=UrlConst.QUERY, params=params)
        if resp.status_code == HTTPStatus.OK:
            return resolve_query_body(resp)
        raise HTTPError(f"create_database error: {resp.status_code}, Response: {resp.text}")

    def create_database_with_rp(self, database: str, rp: RpConfig):
        server_url = self.get_server_url()
        writer = io.StringIO()
        writer.write(f'CREATE DATABASE "{database}" WITH DURATION {rp.duration} REPLICATION 1')
        if len(rp.shard_group_duration) > 0:
            writer.write(f' SHARD DURATION {rp.shard_group_duration}')
        if len(rp.index_duration) > 0:
            writer.write(f' INDEX DURATION {rp.index_duration}')
        writer.write(f' NAME {rp.name}')
        params = {'q': writer.getvalue()}
        writer.close()
        resp = self.request(method='POST', server_url=server_url, url_path=UrlConst.QUERY, params=params)
        if resp.status_code == HTTPStatus.OK:
            return resolve_query_body(resp)
        raise HTTPError(f"create_database_with_rp error: {resp.status_code}, Response: {resp.text}")

    def show_databases(self) -> List[str]:
        qr = self.query(Query(database='', command='SHOW DATABASES', retention_policy=''))
        res = []
        if len(qr.results) == 0 or len(qr.results[0].series) == 0:
            return res
        for database in qr.results[0].series[0].values:
            if len(database) == 0:
                continue
            res.append(database[0])
        return res

    def drop_database(self, database: str):
        server_url = self.get_server_url()
        params = {'q': 'DROP DATABASE ' + database}

        resp = self.request(method='POST', server_url=server_url, url_path=UrlConst.QUERY, params=params)
        if resp.status_code == HTTPStatus.OK:
            return resolve_query_body(resp)
        raise HTTPError(f"drop_database error: {resp.status_code}, Response: {resp.text}")
