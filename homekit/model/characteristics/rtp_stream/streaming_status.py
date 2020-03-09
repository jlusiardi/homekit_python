#
# Copyright 2018-2020 Joachim Lusiardi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import tlv8
from enum import IntEnum
from homekit.model.characteristics import CharacteristicsTypes, CharacteristicPermissions, AbstractTlv8Characteristic, \
    AbstractTlv8CharacteristicValue


class StreamingStatusKey(IntEnum):
    STATUS = 1


class StreamingStatusValue(IntEnum):
    AVAILABLE = 0
    IN_USE = 1
    UNAVAILABLE = 2


class StreamingStatus(AbstractTlv8CharacteristicValue):
    def __init__(self, status: StreamingStatusValue):
        self.status = status

    def to_bytes(self) -> bytes:
        return tlv8.EntryList([tlv8.Entry(StreamingStatusKey.STATUS, self.status)]).encode()

    @staticmethod
    def from_bytes(data: bytes):
        el = tlv8.decode(data, {StreamingStatusKey.STATUS: tlv8.DataType.INTEGER})
        val = el.first_by_id(StreamingStatusKey.STATUS).data
        return __class__(val)


class StreamingStatusCharacteristic(AbstractTlv8Characteristic):
    """
    Defined on page 214
    """

    def __init__(self, iid):
        AbstractTlv8Characteristic.__init__(self, iid, StreamingStatus(StreamingStatusValue.AVAILABLE),
                                            CharacteristicsTypes.STREAMING_STATUS)
        self.perms = [CharacteristicPermissions.paired_read, CharacteristicPermissions.events]
        self.description = 'status of the stream RTP management service'


class StreamingStatusCharacteristicMixin(object):
    def __init__(self, iid):
        self._streamingStatusCharacteristic = StreamingStatusCharacteristic(iid)
        self.characteristics.append(self._streamingStatusCharacteristic)

    def set_streaming_status_get_callback(self, callback):
        self._streamingStatusCharacteristic.set_get_value_callback(callback)
