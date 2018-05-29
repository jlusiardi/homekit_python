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


class CurrentHeatingCoolingStateCharacteristic(AbstractCharacteristic):
    """
    Defined on page 147, valid values:
        0: Off
        1: Heater is on
        2: Cooler is on
    """

    def __init__(self, iid):
        AbstractCharacteristic.__init__(self, iid, CharacteristicsTypes.HEATING_COOLING_CURRENT,
                                        CharacteristicFormats.uint8)
        self.perms = [CharacteristicPermissions.paired_read, CharacteristicPermissions.events]
        self.description = 'Current mode of operation'
        self.minValue = 0
        self.maxValue = 2
        self.minStep = 1
        self.value = 0


class CurrentHeatingCoolingStateCharacteristicMixin(object):
    def __init__(self, iid):
        self._currentHeatingCoolingState = CurrentHeatingCoolingStateCharacteristic(iid)
        self.characteristics.append(self._currentHeatingCoolingState)

    def set_current_heating_cooling_state_get_callback(self, callback):
        self._currentHeatingCoolingState.set_get_value_callback(callback)
