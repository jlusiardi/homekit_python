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
from homekit.model.characteristics.characteristic_permissions import CharacteristicPermissions
from homekit.model.characteristics.characteristic_units import CharacteristicUnits
from homekit.model.characteristics.abstract_characteristic import AbstractCharacteristic


class CurrentTemperatureCharacteristic(AbstractCharacteristic):
    """
    Defined on page 148
    """

    def __init__(self, iid):
        AbstractCharacteristic.__init__(self, iid, CharacteristicsTypes.TEMPERATURE_CURRENT, CharacteristicFormats.float)
        self.perms = [CharacteristicPermissions.paired_read, CharacteristicPermissions.events]
        self.description = 'the current temperature'
        self.minValue = 0.0
        self.maxValue = 100.0
        self.minStep = 0.1
        self.unit = CharacteristicUnits.celsius
        self.value = 23.0


class CurrentTemperatureCharacteristicMixin(object):
    def __init__(self, iid):
        self._currentTemperature = CurrentTemperatureCharacteristic(iid)
        self.characteristics.append(self._currentTemperature)

    def set_on_get_callback(self, callback):
        self._currentTemperature.set_get_value_callback(callback)
