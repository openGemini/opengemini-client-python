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

from requests import HTTPError

from opengemini_client.models import BatchPoints
from opengemini_client.proto import write_pb2, write_pb2_grpc
from opengemini_client.record_transform import RecordTransform


def write(channel, database: str, batch_points: BatchPoints, rp: str = '', username: str = '', password: str = '',
          timeout: int = 0):
    # generate grpc request records
    record_transforms = {}
    for point in batch_points.points:
        rt = record_transforms.get(point.measurement)
        if rt is None:
            rt = RecordTransform()
        rt.add_point(point)
        record_transforms[point.measurement] = rt
    records = []
    for measurement, rt in record_transforms.items():
        record = write_pb2.Record(
            measurement=measurement,
            min_time=rt.min_time,
            max_time=rt.max_time,
            block=rt.convert_to_record().marshal(b''),
        )
        records.append(record)

    # send grpc request
    response = write_pb2_grpc.WriteServiceStub(channel).Write(
        write_pb2.WriteRequest(
            database=database,
            retention_policy=rp,
            username=username,
            password=password,
            records=records,
        ),
        timeout=timeout
    )
    if response.code == 0:
        return
    raise HTTPError(f"write_by_grpc error resp, code: {response.code}")
