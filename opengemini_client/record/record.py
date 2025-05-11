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

from dataclasses import dataclass, field
from typing import List

from opengemini_client.record.colval import ColVal
from opengemini_client.record.field import Field
from opengemini_client.codec.size import size_of_uint32
from opengemini_client.codec.binary_encoder import append_uint32
from opengemini_client.codec.binary_decoder import BinaryDecoder

TimeField = "time"


@dataclass
class Record:
    ColVals: List[ColVal] = field(default_factory=list)
    Fields: List[Field] = field(default_factory=list)

    def marshal(self, buf: bytes) -> bytes:
        # Fields
        buf = append_uint32(buf, len(self.Fields))
        for f in self.Fields:
            buf = append_uint32(buf, f.codec_size())
            buf = f.marshal(buf)

        # ColVals
        buf = append_uint32(buf, len(self.ColVals))
        for col in self.ColVals:
            buf = append_uint32(buf, col.codec_size())
            buf = col.marshal(buf)
        return buf

    def unmarshal(self, buf: bytes):
        if len(buf) == 0:
            return
        dec = BinaryDecoder(buf=buf, offset=0)

        # Fields
        fl = dec.uint32()
        for _ in range(fl):
            fd = Field()
            fd.unmarshal(dec.bytes())
            self.Fields.append(fd)

        # ColVals
        cl = dec.uint32()
        for _ in range(cl):
            col = ColVal()
            col.unmarshal(dec.bytes())
            self.ColVals.append(col)

    def code_size(self) -> int:
        size = 0
        # Fields
        size += size_of_uint32()
        for f in self.Fields:
            size += size_of_uint32()
            size += f.codec_size()

        # ColVals
        size += size_of_uint32()
        for col in self.ColVals:
            size += size_of_uint32()
            size += col.codec_size()
        return size
