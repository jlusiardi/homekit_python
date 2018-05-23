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
from homekit.model.characteristics.abstract_characteristic import AbstractCharacteristic


class TargetHeatingCoolingStateCharacteristic(AbstractCharacteristic):
    """
    Defined on page 161, valid values:
        0: Off
        1: Heat if current temperature is below target temperature
        2: Cool if current temperature is above target temperature
        3: Auto, combination of 1 and 2
    """

    def __init__(self, iid):
        AbstractCharacteristic.__init__(self, iid, CharacteristicsTypes.HEATING_COOLING_TARGET, CharacteristicFormats.uint8)
        self.perms = [CharacteristicPermissions.paired_write, CharacteristicPermissions.paired_read,
                      CharacteristicPermissions.events]
        self.description = 'Desired mode of operation'
        self.minValue = 0
        self.maxValue = 3
        self.minStep = 1
        self.value = 0


class TargetHeatingCoolingStateCharacteristicMixin(object):
    def __init__(self, iid):
        self._targetHeatingCoolingState = TargetHeatingCoolingStateCharacteristic(iid)
        self.characteristics.append(self._targetHeatingCoolingState)

    def set_on_set_callback(self, callback):
        self._targetHeatingCoolingState.set_set_value_callback(callback)

    def set_on_get_callback(self, callback):
        self._targetHeatingCoolingState.set_get_value_callback(callback)
