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
from opengemini_client import Client, Address ,Config, BatchConfig
import datetime

cfg = Config(address=[Address(host='127.0.0.1', port=8086)],
                            batch_config=BatchConfig(batch_size=10, batch_interval=10),
                            timeout=datetime.timedelta(seconds=30), connection_timeout=datetime.timedelta(seconds=10),
                            gzip_enabled=False, tls_enabled=False
                            )

cli = Client(cfg)
cli.ping(0)
```
