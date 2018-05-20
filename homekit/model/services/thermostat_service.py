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

from homekit.model import get_id
from homekit.model.characteristics import CurrentHeatingCoolingStateCharacteristic, \
    TargetHeatingCoolingStateCharacteristic, CurrentTemperatureCharacteristic, TargetTemperatureCharacteristic, \
    TemperatureDisplayUnits
from homekit.model.services.services import _Service, ServicesTypes


class ThermostatService(_Service):
    """
    Defined on page 220
    """

    def __init__(self):
        _Service.__init__(self, ServicesTypes.get_uuid('public.hap.service.thermostat'), get_id())

        self._currentHeatingCoolingState = CurrentHeatingCoolingStateCharacteristic(get_id())
        self.characteristics.append(self._currentHeatingCoolingState)

        self._targetHeatingCoolingState = TargetHeatingCoolingStateCharacteristic(get_id())
        self.characteristics.append(self._targetHeatingCoolingState)

        self._currentTemperature = CurrentTemperatureCharacteristic(get_id())
        self.characteristics.append(self._currentTemperature)

        self._targetTemperature = TargetTemperatureCharacteristic(get_id())
        self.characteristics.append(self._targetTemperature)

        self._temperatureDisplayUnits = TemperatureDisplayUnits(get_id())
        self.characteristics.append(self._temperatureDisplayUnits)

    def set_current_heating_cooling_state_get_callback(self, callback):
        self._currentHeatingCoolingState.set_get_value_callback(callback)

    def set_target_heating_cooling_state_set_callback(self, callback):
        self._targetHeatingCoolingState.set_set_value_callback(callback)

    def set_target_heating_cooling_state_get_callback(self, callback):
        self._targetHeatingCoolingState.set_get_value_callback(callback)

    def set_current_temperature_get_callback(self, callback):
        self._currentTemperature.set_get_value_callback(callback)

    def set_target_temperature_set_callback(self, callback):
        self._targetTemperature.set_set_value_callback(callback)

    def set_target_temperature_get_callback(self, callback):
        self._targetTemperature.set_get_value_callback(callback)

    def set_temperature_display_units_set_callback(self, callback):
        self._temperatureDisplayUnits.set_set_value_callback(callback)

    def set_temperature_display_units_get_callback(self, callback):
        self._temperatureDisplayUnits.set_get_value_callback(callback)