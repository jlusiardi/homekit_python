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
    AbstractCharacteristic


class TemperatureDisplayUnitCharacteristic(AbstractCharacteristic):
    """
    Defined on page 163, valid values:
        0: Celsius
        1: Fahrenheit
    """

    def __init__(self, iid):
        AbstractCharacteristic.__init__(self, iid, CharacteristicsTypes.TEMPERATURE_UNITS, CharacteristicFormats.uint8)
        self.perms = [CharacteristicPermissions.paired_write, CharacteristicPermissions.paired_read,
                      CharacteristicPermissions.events]
        self.description = 'unit of temperature (C/F)'
        self.minValue = 0
        self.maxValue = 1
        self.minStep = 1
        self.value = 0


class TemperatureDisplayUnitsMixin(object):
    def __init__(self, iid):
        self._temperatureDisplayUnits = TemperatureDisplayUnitCharacteristic(iid)
        self.characteristics.append(self._temperatureDisplayUnits)

    def set_temperature_display_units_set_callback(self, callback):
        self._temperatureDisplayUnits.set_set_value_callback(callback)

    def set_temperature_display_units_get_callback(self, callback):
        self._temperatureDisplayUnits.set_get_value_callback(callback)
