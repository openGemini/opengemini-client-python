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

from dataclasses import dataclass
from opengemini_client.codec.size import size_of_string, size_of_int64
from opengemini_client.codec.binary_encoder import append_string, append_int64
from opengemini_client.codec.binary_decoder import BinaryDecoder

Field_Type_Unknown = 0
Field_Type_Int = 1
Field_Type_UInt = 2
Field_Type_Float = 3
Field_Type_String = 4
Field_Type_Boolean = 5
Field_Type_Tag = 6
Field_Type_Last = 7


@dataclass
class Field:
    Type: int = 0
    Name: str = ''

    def marshal(self, buf: bytes) -> bytes:
        buf = append_string(buf, self.Name)
        buf = append_int64(buf, self.Type)
        return buf

    def unmarshal(self, buf: bytes):
        if len(buf) == 0:
            return
        dec = BinaryDecoder(buf=buf, offset=0)
        self.Name = dec.string()
        self.Type = dec.int64()

    def codec_size(self) -> int:
        size = 0
        size += size_of_string(self.Name)
        size += size_of_int64()
        return size
