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

from typing import List

_SizeOfInt16 = 2
_SizeOfInt32 = 4
_SizeOfInt64 = 8

_SizeOfUint8 = 1
_SizeOfUint16 = 2
_SizeOfUint32 = 4
_SizeOfUint64 = 8

_SizeOfFloat32 = 4
_SizeOfFloat64 = 8

_SizeOfBool = 1


def size_of_int16():
    return _SizeOfInt16


def size_of_int32():
    return _SizeOfInt32


def size_of_int64():
    return _SizeOfInt64


def size_of_uint8():
    return _SizeOfUint8


def size_of_uint16():
    return _SizeOfUint16


def size_of_uint32():
    return _SizeOfUint32


def size_of_uint64():
    return _SizeOfUint64


def size_of_float32():
    return _SizeOfFloat32


def size_of_float64():
    return _SizeOfFloat64


def size_of_bool():
    return _SizeOfBool


def size_of_string(s: str) -> int:
    return len(s) + size_of_uint16()


def size_of_bytes(b: bytes) -> int:
    return len(b) + size_of_uint32()


def size_of_uint32_list(v: List[int]) -> int:
    return len(v) * size_of_uint32() + size_of_uint32()
