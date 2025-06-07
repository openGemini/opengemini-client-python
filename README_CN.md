# opengemini-client-python

![License](https://img.shields.io/badge/开源许可证-Apache2.0-green) ![language](https://img.shields.io/badge/语言-Python-blue.svg) [![version](https://img.shields.io/github/v/tag/opengemini/opengemini-client-python?label=%e5%8f%91%e8%a1%8c%e7%89%88%e6%9c%ac&color=blue)](https://github.com/opengemini/opengemini-client-python/releases)

[English](README.md) | 简体中文

`opengemini-client-python` 是一个用 Python 语言编写的 OpenGemini 客户端

## 设计文档

[OpenGemini Client 设计文档](https://github.com/openGemini/openGemini.github.io/blob/main/src/zh/guide/develop/client_design.md)

## 关于 OpenGemini

OpenGemini 是一款云原生分布式时序数据库。获取更多信息，请点击[这里](https://github.com/openGemini/openGemini)

## 要求

- Python 3.9+

## 用法

安装：

```
pip install opengemini_client
```

快速开始：

```python
from opengemini_client import Client, Config, Address

if __name__ == "__main__":
    config = Config(address=[Address(host='127.0.0.1', port=8086)])
    cli = Client(config)
    try:
        cli.ping(0)
        print("ping success")
    except Exception as error:
        print(f"ping failed, {error}")

```

创建数据库：
```python
from opengemini_client import Client, Config, Address

if __name__ == "__main__":
    config = Config(address=[Address(host='127.0.0.1', port=8086)])
    cli = Client(config)
    try:
        database = 'test'
        res = cli.create_database(database=database)
        if res.error is None:
            print(f"create database {database} success")
        else:
            print(f"create database {database} failed, {res.error}")
    except Exception as error:
        print(f"create database {database} failed, {error}")

```

写入points：

```python
from opengemini_client import Client, Config, Address, Point, BatchPoints, Precision

if __name__ == "__main__":
    config = Config(address=[Address(host='127.0.0.1', port=8086)])
    cli = Client(config)
    try:
        database = 'test'
        measurement = 'test_measurement'
        point = Point(
            measurement=measurement,
            precision=Precision.PrecisionSecond,
            fields={'Humidity': 87, 'Temperature': 25},
            tags={'Weather': 'foggy'}
        )
        batch_points = BatchPoints(points=[point])
        cli.write_batch_points(database=database, batch_points=batch_points)
        print(f"write points success")
    except Exception as error:
        print(f"write points failed, {error}")

```

查询：

```python
from opengemini_client import Client, Config, Address, Query

if __name__ == "__main__":
    config = Config(address=[Address(host='127.0.0.1', port=8086)])
    cli = Client(config)
    try:
        database = 'test'
        measurement = 'test_measurement'
        query = Query(
            database=database,
            command=f'select * from {measurement}',
            retention_policy=''
        )
        res = cli.query(query=query)
        if res.error is not None:
            print(f"query error, {res.error}")
        else:
            for result in res.results:
                if result.error is not None:
                    print(f"query result error, {result.error}")
                    continue
                for s in result.series:
                    print(f"name={s.name}, columns={s.columns}, values={s.values}")
    except Exception as error:
        print(f"query failed, {error}")

```

开启TLS(跳过证书认证)：

```python
from opengemini_client import Client, Config, Address, TlsConfig

if __name__ == "__main__":
    config = Config(address=[Address(host='127.0.0.1', port=8443)], tls_enabled=True)
    cli = Client(config)
    try:
        cli.ping(0)
        print("ping success")
    except Exception as error:
        print(f"ping failed, {error}")

```

开启TLS(证书认证)：

```python
import ssl
from opengemini_client import Client, Config, Address, TlsConfig

if __name__ == "__main__":
    context = ssl.SSLContext()
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_verify_locations("ca.crt")
    config = Config(address=[Address(host='127.0.0.1', port=8443)], tls_enabled=True,
                    tls_config=TlsConfig(ca_file="ca.crt"))
    cli = Client(config)
    try:
        cli.ping(0)
        print("ping success")
    except Exception as error:
        print(f"ping failed, {error}")

```

使用grpc协议写入points：
```python
from datetime import datetime
from opengemini_client import Client, Config, Address, Point, BatchPoints, Precision
from opengemini_client.models import GrpcConfig

if __name__ == "__main__":
    config = Config(address=[Address(host='127.0.0.1', port=8086)],
                    grpc_config=GrpcConfig(
                        address=[Address(host='127.0.0.1', port=8305)],
                    ))
    cli = Client(config)
    try:
        database = 'test'
        measurement = 'test_measurement'
        point = Point(
            measurement=measurement,
            precision=Precision.PrecisionSecond,
            fields={'Humidity': 87, 'Temperature': 25},
            tags={'Weather': 'foggy'},
            timestamp=datetime.now(),
        )
        batch_points = BatchPoints(points=[point])
        cli.write_by_grpc(database=database, batch_points=batch_points)
        print(f"write points success")
    except Exception as error:
        print(f"write points failed, {error}")

```
