# Copyright 2025 openGemini Authors
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

import struct
from typing import List
import numpy


def append_int64(b: bytes, v: int) -> bytes:
    v = (numpy.int64(v) << 1) ^ (v >> 63)
    v = numpy.uint64(v)
    u = [numpy.uint8(v >> 56), numpy.uint8(v >> 48), numpy.uint8(v >> 40), numpy.uint8(v >> 32), numpy.uint8(v >> 24),
         numpy.uint8(v >> 16), numpy.uint8(v >> 8), numpy.uint8(v)]
    return b + bytes(u)


def append_uint16(b: bytes, v: int) -> bytes:
    v = numpy.uint16(v)
    u = [numpy.uint8(v >> 8), numpy.uint8(v)]
    return b + bytes(u)


def append_uint32(b: bytes, v: int) -> bytes:
    v = numpy.uint32(v)
    u = [numpy.uint8(v >> 24), numpy.uint8(v >> 16), numpy.uint8(v >> 8), numpy.uint8(v)]
    return b + bytes(u)


def append_string(b: bytes, v: str) -> bytes:
    b = append_uint16(b, len(v))
    return b + v.encode("utf-8")


def append_bytes(b: bytes, v: bytes) -> bytes:
    b = append_uint32(b, len(v))
    return b + v


def append_uint32_list(b: bytes, v: List[int]) -> bytes:
    b = append_uint32(b, len(v))
    if len(v) == 0:
        return b
    byte_data = struct.pack('<' + 'I ' * len(v), *v)
    return b + byte_data
