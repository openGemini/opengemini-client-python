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

引入客户端库：

```
pip install opengemini_client
```

创建客户端:

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
