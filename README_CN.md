# opengemini-client-python

![License](https://img.shields.io/badge/开源许可证-Apache2.0-green) ![language](https://img.shields.io/badge/语言-Python-blue.svg) [![release](https://img.shields.io/github/v/tag/opengemini/opengemini-client-python?label=发行版本&color=blue)](https://github.com/opengemini/opengemini-client-python/releases)

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

<i><font color=gray>示例使用点引用法，用户可结合具体需要选择适合的引用方式。</font></i>

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
