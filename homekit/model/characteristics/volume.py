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

from homekit.model.characteristics import AbstractCharacteristic, CharacteristicFormats, CharacteristicPermissions, \
    CharacteristicUnits, CharacteristicsTypes


class VolumeCharacteristic(AbstractCharacteristic):
    """
    Defined on page 197
    """

    def __init__(self, iid):
        AbstractCharacteristic.__init__(self, iid, CharacteristicsTypes.VOLUME, CharacteristicFormats.uint8)
        self.perms = [CharacteristicPermissions.paired_read, CharacteristicPermissions.paired_write,
                      CharacteristicPermissions.events]
        self.description = 'Volume in percent'
        self.minValue = 0
        self.maxValue = 100
        self.minStep = 1
        self.value = 0
        self.unit = CharacteristicUnits.percentage


class VolumeCharacteristicMixin(object):
    def __init__(self, iid):
        self._volumeCharacteristic = VolumeCharacteristic(iid)
        self.characteristics.append(self._volumeCharacteristic)

    def set_volume_set_callback(self, callback):
        self._volumeCharacteristic.set_set_value_callback(callback)

    def set_volume_get_callback(self, callback):
        self._volumeCharacteristic.set_get_value_callback(callback)
