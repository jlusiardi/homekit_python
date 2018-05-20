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

from homekit.model.characteristics.characteristic_types import CharacteristicsTypes
from homekit.model.characteristics.characteristic_formats import CharacteristicFormats
from homekit.model.characteristics.abstract_characteristic import AbstractCharacteristic


class FirmwareRevisionCharacteristic(AbstractCharacteristic):
    """
    Defined on page 149
    """

    def __init__(self, iid, revision):
        AbstractCharacteristic.__init__(self, iid, CharacteristicsTypes.FIRMWARE_REVISION, CharacteristicFormats.string)
        self.value = revision
        self.description = 'Firmware Revision'
