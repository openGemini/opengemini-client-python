# opengemini-client-python

![License](https://img.shields.io/badge/license-Apache2.0-green) ![Language](https://img.shields.io/badge/Language-Python-blue.svg) [![version](https://img.shields.io/github/v/tag/opengemini/opengemini-client-python?label=release&color=blue)](https://github.com/opengemini/opengemini-client-python/releases)

English | [简体中文](README_CN.md)

`opengemini-client-python` is a Python client for OpenGemini

## Design Doc

[OpenGemini Client Design Doc](https://github.com/openGemini/openGemini.github.io/blob/main/src/guide/develop/client_design.md)

## About OpenGemini

OpenGemini is a cloud-native distributed time series database, find more information [here](https://github.com/openGemini/openGemini)

## Requirements

- Python 3.9+

## Usage

Install:

```
pip install opengemini_client
```
Getting Started：

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

Create a database：
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

Write points：

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

Do a query：

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
