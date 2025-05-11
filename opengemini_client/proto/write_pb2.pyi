from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CompressMethod(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNCOMPRESSED: _ClassVar[CompressMethod]
    LZ4_FAST: _ClassVar[CompressMethod]
    ZSTD_FAST: _ClassVar[CompressMethod]
    SNAPPY: _ClassVar[CompressMethod]

class ResponseCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Success: _ClassVar[ResponseCode]
    Partial: _ClassVar[ResponseCode]
    Failed: _ClassVar[ResponseCode]

class ServerStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Up: _ClassVar[ServerStatus]
    Down: _ClassVar[ServerStatus]
    Unknown: _ClassVar[ServerStatus]
UNCOMPRESSED: CompressMethod
LZ4_FAST: CompressMethod
ZSTD_FAST: CompressMethod
SNAPPY: CompressMethod
Success: ResponseCode
Partial: ResponseCode
Failed: ResponseCode
Up: ServerStatus
Down: ServerStatus
Unknown: ServerStatus

class WriteRequest(_message.Message):
    __slots__ = ("version", "database", "retention_policy", "username", "password", "records")
    VERSION_FIELD_NUMBER: _ClassVar[int]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    RETENTION_POLICY_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    RECORDS_FIELD_NUMBER: _ClassVar[int]
    version: int
    database: str
    retention_policy: str
    username: str
    password: str
    records: _containers.RepeatedCompositeFieldContainer[Record]
    def __init__(self, version: _Optional[int] = ..., database: _Optional[str] = ..., retention_policy: _Optional[str] = ..., username: _Optional[str] = ..., password: _Optional[str] = ..., records: _Optional[_Iterable[_Union[Record, _Mapping]]] = ...) -> None: ...

class WriteResponse(_message.Message):
    __slots__ = ("code",)
    CODE_FIELD_NUMBER: _ClassVar[int]
    code: ResponseCode
    def __init__(self, code: _Optional[_Union[ResponseCode, str]] = ...) -> None: ...

class Record(_message.Message):
    __slots__ = ("measurement", "min_time", "max_time", "compress_method", "block")
    MEASUREMENT_FIELD_NUMBER: _ClassVar[int]
    MIN_TIME_FIELD_NUMBER: _ClassVar[int]
    MAX_TIME_FIELD_NUMBER: _ClassVar[int]
    COMPRESS_METHOD_FIELD_NUMBER: _ClassVar[int]
    BLOCK_FIELD_NUMBER: _ClassVar[int]
    measurement: str
    min_time: int
    max_time: int
    compress_method: CompressMethod
    block: bytes
    def __init__(self, measurement: _Optional[str] = ..., min_time: _Optional[int] = ..., max_time: _Optional[int] = ..., compress_method: _Optional[_Union[CompressMethod, str]] = ..., block: _Optional[bytes] = ...) -> None: ...

class PingRequest(_message.Message):
    __slots__ = ("client_id",)
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    client_id: str
    def __init__(self, client_id: _Optional[str] = ...) -> None: ...

class PingResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: ServerStatus
    def __init__(self, status: _Optional[_Union[ServerStatus, str]] = ...) -> None: ...
