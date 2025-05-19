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
from dataclasses import dataclass
from typing import List
import numpy
from opengemini_client.codec.size import size_of_int64, size_of_uint16, size_of_uint32


@dataclass
class BinaryDecoder:
    buf: 'bytes' = b''
    offset: int = 0

    def int64(self) -> int:
        u = self.buf[self.offset:self.offset + size_of_int64()]
        v = u[7] | u[6] << 8 | u[5] << 16 | u[4] << 24 | u[3] << 32 | u[2] << 40 | u[1] << 48 | u[0] << 56
        v = (numpy.int64(v) >> 1) ^ ((numpy.int64(v) << 63) >> 63)
        self.offset += size_of_int64()
        return int(v)

    def uint16(self) -> int:
        u = self.buf[self.offset:self.offset + size_of_uint16()]
        v = u[1] | u[0] << 8
        self.offset += size_of_uint16()
        return int(v)

    def uint32(self) -> int:
        u = self.buf[self.offset:self.offset + size_of_uint32()]
        v = u[3] | u[2] << 8 | u[1] << 16 | u[0] << 24
        self.offset += size_of_uint32()
        return int(v)

    def string(self) -> str:
        length = self.uint16()
        v = self.buf[self.offset:self.offset + length].decode("utf-8")
        self.offset += length
        return v

    def bytes(self) -> bytes:
        length = self.uint32()
        if length == 0:
            return b''
        v = self.buf[self.offset:self.offset + length]
        self.offset += length
        return v

    def uint32_list(self) -> List[int]:
        length = self.uint32()
        if length == 0:
            return []
        length1 = length * size_of_uint32()
        v = struct.unpack('<' + 'I ' * length, self.buf[self.offset:self.offset + length1])
        self.offset += length1
        return [int(i) for i in v]
