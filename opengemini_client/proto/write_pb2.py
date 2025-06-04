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

from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    28,
    1,
    '',
    'write.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0bwrite.proto\x12\x05proto\"\x8f\x01\n\x0cWriteRequest\x12\x0f\n\x07version\x18\x01 \x01(\r\x12\x10\n\x08\x64\x61tabase\x18\x02 \x01(\t\x12\x18\n\x10retention_policy\x18\x03 \x01(\t\x12\x10\n\x08username\x18\x04 \x01(\t\x12\x10\n\x08password\x18\x05 \x01(\t\x12\x1e\n\x07records\x18\x06 \x03(\x0b\x32\r.proto.Record\"2\n\rWriteResponse\x12!\n\x04\x63ode\x18\x01 \x01(\x0e\x32\x13.proto.ResponseCode\"\x80\x01\n\x06Record\x12\x13\n\x0bmeasurement\x18\x01 \x01(\t\x12\x10\n\x08min_time\x18\x02 \x01(\x03\x12\x10\n\x08max_time\x18\x03 \x01(\x03\x12.\n\x0f\x63ompress_method\x18\x04 \x01(\x0e\x32\x15.proto.CompressMethod\x12\r\n\x05\x62lock\x18\x05 \x01(\x0c\" \n\x0bPingRequest\x12\x11\n\tclient_id\x18\x01 \x01(\t\"3\n\x0cPingResponse\x12#\n\x06status\x18\x01 \x01(\x0e\x32\x13.proto.ServerStatus*K\n\x0e\x43ompressMethod\x12\x10\n\x0cUNCOMPRESSED\x10\x00\x12\x0c\n\x08LZ4_FAST\x10\x01\x12\r\n\tZSTD_FAST\x10\x02\x12\n\n\x06SNAPPY\x10\x03*4\n\x0cResponseCode\x12\x0b\n\x07Success\x10\x00\x12\x0b\n\x07Partial\x10\x01\x12\n\n\x06\x46\x61iled\x10\x02*-\n\x0cServerStatus\x12\x06\n\x02Up\x10\x00\x12\x08\n\x04\x44own\x10\x01\x12\x0b\n\x07Unknown\x10\x63\x32w\n\x0cWriteService\x12\x34\n\x05Write\x12\x13.proto.WriteRequest\x1a\x14.proto.WriteResponse\"\x00\x12\x31\n\x04Ping\x12\x12.proto.PingRequest\x1a\x13.proto.PingResponse\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'write_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_COMPRESSMETHOD']._serialized_start=438
  _globals['_COMPRESSMETHOD']._serialized_end=513
  _globals['_RESPONSECODE']._serialized_start=515
  _globals['_RESPONSECODE']._serialized_end=567
  _globals['_SERVERSTATUS']._serialized_start=569
  _globals['_SERVERSTATUS']._serialized_end=614
  _globals['_WRITEREQUEST']._serialized_start=23
  _globals['_WRITEREQUEST']._serialized_end=166
  _globals['_WRITERESPONSE']._serialized_start=168
  _globals['_WRITERESPONSE']._serialized_end=218
  _globals['_RECORD']._serialized_start=221
  _globals['_RECORD']._serialized_end=349
  _globals['_PINGREQUEST']._serialized_start=351
  _globals['_PINGREQUEST']._serialized_end=383
  _globals['_PINGRESPONSE']._serialized_start=385
  _globals['_PINGRESPONSE']._serialized_end=436
  _globals['_WRITESERVICE']._serialized_start=616
  _globals['_WRITESERVICE']._serialized_end=735
# @@protoc_insertion_point(module_scope)
