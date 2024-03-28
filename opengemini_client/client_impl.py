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


def resolve_query_body(resp: requests.Response):
    json_data = resp.json()
    results = [
        SeriesResult(
            series=[
                Series(
                    name=series.get('name', ''),
                    columns=series.get('columns', []),
                    values=series.get('values', [])
                )
                for series in result.get('series', [])
                if series.get('values', [])
            ],
            error=result.get('error')
        )
        for result in json_data.get('results', [])
    ]
    return QueryResult(results=results, error=json_data.get('error'))


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
            raise HTTPError(f"Query error_code: {resp.status_code}, error_msg: {resp.text}")
        return resp

    def exec_http_request_by_index(self, idx, method, url_path, headers=None, body=None) -> requests.Response:
        if idx >= len(self.endpoints) or idx < 0:
            raise ValueError("openGeminiDB client error. Index out of range")
        return self.request(method, self.endpoints[idx], url_path, headers, body)

    def ping(self, idx: int):
        resp = self.exec_http_request_by_index(idx, 'GET', UrlConst.PING)
        if resp.status_code != HTTPStatus.NO_CONTENT:
            raise HTTPError(f"Query error_code: {resp.status_code}, error_msg: {resp.text}")

    def query(self, query: Query) -> QueryResult:
        server_url = self.get_server_url()
        params = {'db': query.database, 'q': query.command, 'rp': query.retention_policy}

        resp = self.request(method='GET', server_url=server_url, url_path=UrlConst.QUERY, params=params)
        if resp.status_code == HTTPStatus.OK:
            return resolve_query_body(resp)
        raise HTTPError(f"Query error_code: {resp.status_code}, error_msg: {resp.text}")

    def _query_post(self, query: Query) -> QueryResult:
        server_url = self.get_server_url()
        params = {'db': query.database, 'q': query.command, 'rp': query.retention_policy}

        resp = self.request(method='POST', server_url=server_url, url_path=UrlConst.QUERY, params=params)
        if resp.status_code == HTTPStatus.OK:
            return resolve_query_body(resp)
        raise HTTPError(f"Query error_code: {resp.status_code}, error_msg: {resp.text}")

    def write_batch_points(self, database: str, batch_points: BatchPoints):
        return

    def create_database(self, database, rp: RpConfig = None):
        if len(database) == 0:
            raise ValueError("empty database name")
        if rp is None:
            query_string = f"CREATE DATABASE {str(database).strip()}"
        else:
            query_string = f"CREATE DATABASE {str(database).strip()} WITH DURATION {rp.duration} REPLICATION 1"
            if len(rp.shard_group_duration) > 0:
                query_string += f" SHARD DURATION {rp.shard_group_duration.strip()}"
            if len(rp.index_duration) > 0:
                query_string += f" INDEX DURATION {rp.index_duration.strip()}"
            if len(rp.name) > 0:
                query_string += f" NAME {rp.name.strip()}"
        return self._query_post(Query(database=str(database).strip(), command=query_string, retention_policy=''))

    def show_databases(self) -> List[str]:
        databases = []
        query_string = "SHOW DATABASES"
        qr = self.query(Query(database='', command=query_string, retention_policy=''))
        if len(qr.results) == 0 or len(qr.results[0].series) == 0:
            return databases
        databases = [val[0] for val in qr.results[0].series[0].values if len(val) > 0]
        return databases

    def drop_database(self, database):
        if len(database) == 0:
            raise ValueError("empty database name")
        query_string = f"DROP DATABASE {str(database).strip()}"
        return self._query_post(Query(database=str(database).strip(), command=query_string, retention_policy=''))

    def create_retention_policy(self, dbname, rp_config: RpConfig, is_default: bool):
        if len(dbname) == 0:
            raise ValueError("empty database name")
        if rp_config is None:
            raise ValueError("rp_config is required")

        query_string = (
            f"CREATE RETENTION POLICY {rp_config.name} ON {str(dbname).strip()} DURATION {rp_config.duration}"
            f" REPLICATION 1 ")

        if len(rp_config.shard_group_duration) > 0:
            query_string += f" SHARD DURATION {rp_config.shard_group_duration}"

        if len(rp_config.index_duration) > 0:
            query_string += f" INDEX DURATION {rp_config.index_duration}"

        if is_default:
            query_string += " DEFAULT"

        return self._query_post(Query(database=str(dbname).strip(), command=query_string, retention_policy=''))

    def show_retention_policies(self, dbname):
        if len(dbname) == 0:
            raise ValueError("empty database name")

        query_string = f"SHOW RETENTION POLICIES ON {str(dbname).strip()}"
        qr = self.query(Query(database=str(dbname).strip(), command=query_string, retention_policy=''))
        retention_polices = []
        if len(qr.results) == 0 or len(qr.results[0].series) == 0:
            return retention_polices
        retention_polices = [val for val in qr.results[0].series[0].values if len(val) > 0]
        return retention_polices

    def drop_retention_policy(self, dbname, retention_policy: str):
        if len(dbname) == 0:
            raise ValueError("empty database name")
        if len(retention_policy) == 0:
            raise ValueError("empty retention policy name")

        query_string = f"DROP RETENTION POLICY {str(retention_policy).strip()} ON {str(dbname).strip()}"
        return self._query_post(Query(database=str(dbname).strip(), command=query_string,
                                      retention_policy=str(retention_policy).strip()))
