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


class TargetTemperatureCharacteristic(AbstractCharacteristic):
    """
    Defined on page 162
    """

    def __init__(self, iid):
        AbstractCharacteristic.__init__(self, iid, CharacteristicsTypes.TEMPERATURE_TARGET, CharacteristicFormats.float)
        self.perms = [CharacteristicPermissions.paired_write, CharacteristicPermissions.paired_read,
                      CharacteristicPermissions.events]
        self.description = 'the desired temperature'
        self.minValue = 10.0
        self.maxValue = 38.0
        self.minStep = 0.1
        self.unit = CharacteristicUnits.celsius
        self.value = 23.0


class TargetTemperatureCharacteristicMixin(object):
    def __init__(self, iid):
        self._targetTemperature = TargetTemperatureCharacteristic(iid)
        self.characteristics.append(self._targetTemperature)

    def set_target_temperature_set_callback(self, callback):
        self._targetTemperature.set_set_value_callback(callback)

    def set_target_temperature_get_callback(self, callback):
        self._targetTemperature.set_get_value_callback(callback)
