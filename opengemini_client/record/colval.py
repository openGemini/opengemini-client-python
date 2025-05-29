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
from dataclasses import dataclass, field
from typing import List
from opengemini_client.codec.binary_encoder import (append_int64, append_bytes, append_uint32_list)
from opengemini_client.codec.binary_decoder import BinaryDecoder
from opengemini_client.codec.size import size_of_int64, size_of_bytes, size_of_uint32_list

_BitMask = [1, 2, 4, 8, 16, 32, 64, 128]
_FlippedBitMask = [254, 253, 251, 247, 239, 223, 191, 127]


@dataclass
class ColVal:
    Val: bytes = b''
    Offset: List[int] = field(default_factory=list)
    Bitmap: bytes = b''
    BitmapOffset: int = 0
    Len: int = 0
    NilCount: int = 0

    def _set_bitmap(self, index: int):
        if (self.Len + self.BitmapOffset) >> 3 >= len(self.Bitmap):
            self.Bitmap += struct.pack('<B', 1)
            return
        index += self.BitmapOffset
        index1 = index >> 3
        self.Bitmap = (self.Bitmap[:index1] + bytes([self.Bitmap[index1] | _BitMask[index & 0x07]]) +
                       self.Bitmap[index1 + 1:])

    def _reset_bitmap(self, index: int):
        if (self.Len + self.BitmapOffset) >> 3 >= len(self.Bitmap):
            self.Bitmap = struct.pack('<B', 0)
            return
        index += self.BitmapOffset
        index1 = index >> 3
        self.Bitmap = (self.Bitmap[:index1] + bytes([self.Bitmap[index1] & _FlippedBitMask[index & 0x07]]) +
                       self.Bitmap[index1 + 1:])

    def _append_null(self):
        self._reset_bitmap(self.Len)
        self.Len += 1
        self.NilCount += 1

    def append_integer(self, v: int):
        self.Val += struct.pack('<q', v)
        self._set_bitmap(self.Len)
        self.Len += 1

    def append_integer_null(self):
        self._append_null()

    def append_integer_nulls(self, count):
        for _ in range(count):
            self.append_integer_null()

    def append_boolean(self, v: bool):
        if v:
            self.Val += struct.pack('<B', 1)
        else:
            self.Val += struct.pack('<B', 0)
        self._set_bitmap(self.Len)
        self.Len += 1

    def append_boolean_null(self):
        self._append_null()

    def append_boolean_nulls(self, count):
        for _ in range(count):
            self.append_boolean_null()

    def append_float(self, v: float):
        self.Val += struct.pack('<d', v)
        self._set_bitmap(self.Len)
        self.Len += 1

    def append_float_null(self):
        self._append_null()

    def append_float_nulls(self, count):
        for _ in range(count):
            self.append_float_null()

    def append_string(self, v: str):
        index = len(self.Val)
        self.Val += v.encode("utf-8")
        self.Offset.append(index)
        self._set_bitmap(self.Len)
        self.Len += 1

    def append_string_null(self):
        self.Offset.append(len(self.Val))
        self._append_null()

    def append_string_nulls(self, count):
        for _ in range(count):
            self.append_string_null()

    def marshal(self, buf: bytes) -> bytes:
        buf = append_int64(buf, self.Len)
        buf = append_int64(buf, self.NilCount)
        buf = append_int64(buf, self.BitmapOffset)
        buf = append_bytes(buf, self.Val)
        buf = append_bytes(buf, self.Bitmap)
        buf = append_uint32_list(buf, self.Offset)
        return buf

    def unmarshal(self, buf: bytes):
        if len(buf) == 0:
            return
        dec = BinaryDecoder(buf=buf, offset=0)
        self.Len = dec.int64()
        self.NilCount = dec.int64()
        self.BitmapOffset = dec.int64()
        self.Val = dec.bytes()
        self.Bitmap = dec.bytes()
        self.Offset = dec.uint32_list()

    def codec_size(self) -> int:
        size = 0
        # Len
        size += size_of_int64()
        # NilCount
        size += size_of_int64()
        # BitmapOffset
        size += size_of_int64()
        # Val
        size += size_of_bytes(self.Val)
        # Bitmap
        size += size_of_bytes(self.Bitmap)
        # Offset
        size += size_of_uint32_list(self.Offset)
        return size
