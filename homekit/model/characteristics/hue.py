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

from homekit.model.characteristics import CharacteristicsTypes, CharacteristicFormats, CharacteristicPermissions, \
    AbstractCharacteristic, CharacteristicUnits


class HueCharacteristic(AbstractCharacteristic):
    """
    Defined on page 151
    """

    def __init__(self, iid):
        AbstractCharacteristic.__init__(self, iid, CharacteristicsTypes.HUE, CharacteristicFormats.float)
        self.perms = [CharacteristicPermissions.paired_read, CharacteristicPermissions.paired_write,
                      CharacteristicPermissions.events]
        self.description = 'Hue in arc degrees'
        self.minValue = 0
        self.maxValue = 360
        self.minStep = 1
        self.value = 0
        self.unit = CharacteristicUnits.arcdegrees


class HueCharacteristicMixin(object):
    def __init__(self, iid):
        self._hueCharacteristic = HueCharacteristic(iid)
        self.characteristics.append(self._hueCharacteristic)

    def set_hue_set_callback(self, callback):
        self._hueCharacteristic.set_set_value_callback(callback)

    def set_brightness_get_callback(self, callback):
        self._hueCharacteristic.set_get_value_callback(callback)
