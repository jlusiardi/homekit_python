#
# Copyright 2018 Joachim Lusiardi
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

from enum import IntEnum
from homekit.model.characteristics import CharacteristicsTypes, CharacteristicFormats, CharacteristicPermissions, \
    AbstractCharacteristic
from homekit.protocol.tlv import TLVItem


class StreamingStatusEnum(IntEnum):
    AVAILABLE = 0
    IN_USE = 1
    UNAVAILABLE = 2


class StreamingStatus:
    status = TLVItem(1, StreamingStatusEnum)

    def __init__(self, status):
        self.status = status


class StreamingStatusCharacteristic(AbstractCharacteristic):
    """
    Defined on page 214
    """

    def __init__(self, iid):
        AbstractCharacteristic.__init__(self, iid, CharacteristicsTypes.STREAMING_STATUS, CharacteristicFormats.tlv8,
                                        StreamingStatus)
        self.perms = [CharacteristicPermissions.paired_read, CharacteristicPermissions.events]
        self.description = 'status of the stream RTP management service'
        self.value = StreamingStatus(StreamingStatusEnum.AVAILABLE)


class StreamingStatusCharacteristicMixin(object):
    def __init__(self, iid):
        self._streamingStatusCharacteristic = StreamingStatusCharacteristic(iid)
        self.characteristics.append(self._streamingStatusCharacteristic)

    def set_streaming_status_get_callback(self, callback):
        self._streamingStatusCharacteristic.set_get_value_callback(callback)
