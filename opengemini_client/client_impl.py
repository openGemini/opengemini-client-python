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

import base64
import datetime
import gzip
import io
import itertools
from abc import ABC
from http import HTTPStatus
from typing import List

import requests
from requests import HTTPError

from opengemini_client.client import Client
from opengemini_client.measurement import Measurement, MeasurementCondition
from opengemini_client.models import Config, BatchPoints, Query, QueryResult, Series, SeriesResult, RpConfig, \
    ValuesResult, KeyValue
from opengemini_client.url_const import UrlConst
from opengemini_client.models import AuthType, TlsConfig


def check_config(config: Config):
    if len(config.address) == 0:
        raise ValueError("must have at least one address")

    if config.auth_config is not None:
        if config.auth_config.auth_type == AuthType.PASSWORD:
            if len(config.auth_config.username) == 0:
                raise ValueError("invalid auth config due to empty username")
            if len(config.auth_config.password) == 0:
                raise ValueError("invalid auth config due to empty password")
        if config.auth_config.auth_type == AuthType.TOKEN and len(config.auth_config.token) == 0:
            raise ValueError("invalid auth config due to empty token")

    if config.tls_enabled and config.tls_config is None:
        config.tls_config = TlsConfig()

    if config.batch_config is not None:
        if config.batch_config.batch_interval <= 0:
            raise ValueError("batch enabled,batch interval must be greater than 0")
        if config.batch_config.batch_size <= 0:
            raise ValueError("batch enabled,batch size must be greater than 0")

    if config.timeout is None or config.timeout <= datetime.timedelta(seconds=0):
        config.timeout = datetime.timedelta(seconds=30)

    if config.connection_timeout is None or config.connection_timeout <= datetime.timedelta(seconds=0):
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

    def __init__(self, config: Config):
        self.config = check_config(config)
        self.session = requests.Session()
        protocol = "http://"
        if config.tls_enabled:
            protocol = "https://"
            self.session.cert = (config.tls_config.cert_file, config.tls_config.key_file)
            self.session.verify = config.tls_config.ca_file
        self.endpoints = [f"{protocol}{addr.host}:{addr.port}" for addr in config.address]
        self.endpoints_iter = itertools.cycle(self.endpoints)

    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        self.session.close()

    def _get_server_url(self):
        return next(self.endpoints_iter)

    def _update_headers(self, method, url_path, headers=None) -> dict:
        if headers is None:
            headers = {}

        if not self.config.auth_config:
            return headers

        if url_path in UrlConst.no_auth_required:
            if method in UrlConst.no_auth_required[url_path]:
                return headers

        if self.config.auth_config.auth_type == AuthType.PASSWORD:
            encode_string = f"{self.config.auth_config.username}:{self.config.auth_config.password}"
            authorization = "Basic " + base64.b64encode(encode_string.encode()).decode()
            headers["Authorization"] = authorization

        if self.config.gzip_enabled:
            headers.update({"Content-Encoding": "gzip", "Accept-Encoding": "gzip"})

        return headers

    def _request(self, method, server_url, url_path, headers=None, body=None, params=None) -> requests.Response:
        if params is None:
            params = {}
        headers = self._update_headers(method, url_path, headers)
        full_url = server_url + url_path
        if self.config.gzip_enabled and body is not None:
            compressed = io.BytesIO()
            with gzip.GzipFile(compresslevel=9, fileobj=compressed, mode='w') as f:
                f.write(body)
                body = compressed.getvalue()

        req = requests.Request(method, full_url, data=body, headers=headers, params=params)
        prepared = req.prepare()
        timeout = (self.config.connection_timeout.seconds, self.config.timeout.seconds)
        resp = self.session.send(prepared, timeout=timeout)
        if not 200 <= resp.status_code < 300:
            raise HTTPError(f"request error resp, code: {resp.status_code}, body: {resp.text}")
        return resp

    def _exec_http_request_by_index(self, idx, method, url_path, headers=None, body=None) -> requests.Response:
        if idx >= len(self.endpoints) or idx < 0:
            raise ValueError("openGeminiDB client error. Index out of range")
        return self._request(method, self.endpoints[idx], url_path, headers, body)

    def ping(self, idx: int):
        resp = self._exec_http_request_by_index(idx, 'GET', UrlConst.PING)
        if resp.status_code != HTTPStatus.NO_CONTENT:
            raise HTTPError(f"ping error resp, code: {resp.status_code}, body: {resp.text}")

    def query(self, query: Query) -> QueryResult:
        server_url = self._get_server_url()
        params = {'db': query.database, 'q': query.command, 'rp': query.retention_policy,
                  'epoch': query.precision.epoch()}

        resp = self._request(method='GET', server_url=server_url, url_path=UrlConst.QUERY, params=params)
        if resp.status_code == HTTPStatus.OK:
            return resolve_query_body(resp)
        raise HTTPError(f"query error resp, code: {resp.status_code}, body: {resp.text}")

    def _query_post(self, query: Query) -> QueryResult:
        server_url = self._get_server_url()
        params = {'db': query.database, 'q': query.command, 'rp': query.retention_policy}

        resp = self._request(method='POST', server_url=server_url, url_path=UrlConst.QUERY, params=params)
        if resp.status_code == HTTPStatus.OK:
            return resolve_query_body(resp)
        raise HTTPError(f"query_post error resp, code: {resp.status_code}, body: {resp.text}")

    def write_batch_points(self, database: str, batch_points: BatchPoints):
        server_url = self._get_server_url()
        params = {'db': database}
        with io.StringIO() as writer:
            for point in batch_points.points:
                if point is None:
                    continue
                writer.write(point.to_string())
                writer.write('\n')
            body = writer.getvalue().encode()
        resp = self._request(method="POST", server_url=server_url, url_path=UrlConst.WRITE, params=params, body=body)
        if resp.status_code == HTTPStatus.NO_CONTENT:
            return
        raise HTTPError(f"write_batch_points error resp, code: {resp.status_code}, body: {resp.text}")

    def create_database(self, database: str, rp: RpConfig = None):
        if not database:
            raise ValueError("empty database name")
        query_string = f"CREATE DATABASE {database}"
        if rp:
            query_string += f" WITH DURATION {rp.duration} REPLICATION 1"
            if rp.shard_group_duration:
                query_string += f" SHARD DURATION {rp.shard_group_duration}"
            if rp.index_duration:
                query_string += f" INDEX DURATION {rp.index_duration}"
            if rp.name:
                query_string += f" NAME {rp.name}"
        return self._query_post(Query(database=database, command=query_string, retention_policy=''))

    def show_databases(self) -> List[str]:
        query_string = "SHOW DATABASES"
        qr = self.query(Query(database='', command=query_string, retention_policy=''))
        if not qr.results or not qr.results[0].series:
            return []
        return [val[0] for val in qr.results[0].series[0].values if val]

    def drop_database(self, database: str):
        if not database:
            raise ValueError("empty database name")
        query_string = f"DROP DATABASE {database}"
        return self._query_post(Query(database=database, command=query_string, retention_policy=''))

    def create_retention_policy(self, dbname, rp_config: RpConfig, is_default: bool):
        if not dbname:
            raise ValueError("empty database name")
        if not rp_config:
            raise ValueError("rp_config is required")

        query_string = (f"CREATE RETENTION POLICY {rp_config.name} ON {dbname} DURATION {rp_config.duration}"
                        f" REPLICATION 1")
        if rp_config.shard_group_duration:
            query_string += f" SHARD DURATION {rp_config.shard_group_duration}"
        if rp_config.index_duration:
            query_string += f" INDEX DURATION {rp_config.index_duration}"
        if is_default:
            query_string += " DEFAULT"

        return self._query_post(Query(database=dbname, command=query_string, retention_policy=''))

    def show_retention_policies(self, dbname: str):
        if not dbname:
            raise ValueError("empty database name")

        query_string = f"SHOW RETENTION POLICIES ON {dbname}"
        qr = self.query(Query(database=dbname, command=query_string, retention_policy=''))
        if not qr.results or not qr.results[0].series:
            return []
        return [val for val in qr.results[0].series[0].values if val]

    def drop_retention_policy(self, dbname, retention_policy: str):
        if not dbname:
            raise ValueError("empty database name")
        if not retention_policy:
            raise ValueError("empty retention policy name")

        query_string = f"DROP RETENTION POLICY {retention_policy} ON {dbname}"
        return self._query_post(Query(database=dbname, command=query_string, retention_policy=retention_policy))

    def _show_query_result(self, database, command: str) -> QueryResult:
        if not database:
            raise ValueError("empty database name")
        if not command:
            raise ValueError("empty query command")
        return self.query(query=Query(database=database, command=command, retention_policy=''))

    def _show_with_result_any(self, database, command: str) -> List[ValuesResult]:
        values_results = []
        query_results = self._show_query_result(database, command)
        if len(query_results.results) == 0:
            return values_results
        for res in query_results.results[0].series:
            values_result = ValuesResult(measurement=res.name, values=[])
            for values in res.values:
                for value in values:
                    values_result.values.append(value)
            values_results.append(values_result)
        return values_results

    def _show_with_result_key_value(self, database, command: str) -> List[ValuesResult]:
        values_results = []
        query_results = self._show_query_result(database, command)
        if len(query_results.results) == 0:
            return values_results
        for res in query_results.results[0].series:
            values_result = ValuesResult(measurement=res.name, values=[])
            for values in res.values:
                if len(values) < 2:
                    continue
                values_result.values.append(KeyValue(name=values[0], value=values[1]))
            values_results.append(values_result)
        return values_results

    def create_measurement(self, measurement: Measurement):
        if measurement is None:
            raise ValueError("empty measurement")
        measurement.check()
        command = measurement.to_string()
        return self._query_post(Query(database=measurement.database, command=command, retention_policy=''))

    def show_measurements(self, condition: MeasurementCondition) -> List[str]:
        if condition is None:
            raise ValueError("empty measurement condition")
        condition.check()
        command = condition.to_string()
        result = self.query(Query(database=condition.database, command=command, retention_policy=''))
        if result.error is not None:
            raise HTTPError(f"show_measurements error result, error: {result.error}")
        measurements = []
        if len(result.results) == 0 or len(result.results[0].series) == 0:
            return measurements
        if result.results[0].error is not None:
            raise HTTPError(f"show_measurements error result, error: {result.results[0].error}")
        for v in result.results[0].series[0].values:
            if isinstance(v[0], str):
                measurements.append(str(v[0]))
        return measurements

    def drop_measurement(self, database: str, retention_policy: str, measurement: str):
        if not database:
            raise ValueError("empty database name")
        if not measurement:
            raise ValueError("empty measurement name")
        command = f"DROP MEASUREMENT {measurement}"
        return self._query_post(Query(database=database, command=command, retention_policy=retention_policy))

    def show_tag_keys(self, database, command: str) -> List[ValuesResult]:
        return self._show_with_result_any(database, command)

    def show_tag_values(self, database, command: str) -> List[ValuesResult]:
        return self._show_with_result_key_value(database, command)

    def show_field_keys(self, database, command: str) -> List[ValuesResult]:
        return self._show_with_result_key_value(database, command)

    def show_series(self, database, command: str) -> List[str]:
        values_result = self._show_with_result_any(database, command)
        series = []
        if len(values_result) == 0:
            return series
        for value in values_result[0].values:
            if isinstance(value, str):
                series.append(value)
        return series
