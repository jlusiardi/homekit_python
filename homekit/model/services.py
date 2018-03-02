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

from homekit.model.characteristics import *


class _ServicesTypes(object):
    """
    This data is taken from Table 12-3 Accessory Categories on page 254. Values above 19 are reserved.
    """

    def __init__(self):
        self.baseUUID = '-0000-1000-8000-0026BB765291'
        self._services = {
            '3E': 'public.hap.service.accessory-information',
            '40': 'public.hap.service.fan',
            '41': 'public.hap.service.garage-door-opener',
            '43': 'public.hap.service.lightbulb',
            '44': 'public.hap.service.lock-management',
            '45': 'public.hap.service.lock-mechanism',
            '47': 'public.hap.service.outlet',
            '49': 'public.hap.service.switch',
            '4A': 'public.hap.service.thermostat',
            '7E': 'public.hap.service.security-system',
            '7F': 'public.hap.service.sensor.carbon-monoxide',
            '80': 'public.hap.service.sensor.contact',
            '81': 'public.hap.service.door',
            '82': 'public.hap.service.sensor.humidity',
            '83': 'public.hap.service.sensor.leak',
            '84': 'public.hap.service.sensor.light',
            '85': 'public.hap.service.sensor.motion',
            '86': 'public.hap.service.sensor.occupancy',
            '87': 'public.hap.service.sensor.smoke',
            '89': 'public.hap.service.stateless-programmable-switch',
            '8A': 'public.hap.service.sensor.temperature',
            '8B': 'public.hap.service.window',
            '8C': 'public.hap.service.window-covering',
            '8D': 'public.hap.service.sensor.air-quality',
            '96': 'public.hap.service.battery',
            '97': 'public.hap.service.sensor.carbon-dioxide',
            'B7': 'public.hap.service.fanv2',
            'B9': 'public.hap.service.vertical-slat',
            'BA': 'public.hap.service.filter-maintenance',
            'BB': 'public.hap.service.air-purifier',
            'CC': 'public.hap.service.service-label',
            '110': 'public.hap.service.camera-rtp-stream-management',
            '112': 'public.hap.service.microphone',
            '113': 'public.hap.service.speaker',
            '121': 'public.hap.service.doorbell',
        }

        self._services_rev = {self._services[k]: k for k in self._services.keys()}

    def __getitem__(self, item):
        if item in self._services:
            return self._services[item]

        if item in self._services_rev:
            return self._services_rev[item]

        # raise KeyError('Item {item} not found'.format_map(item=item))
        return 'Unknown Service: {i}'.format(i=item)

    def get_short(self, item):
        orig_item = item
        if item.endswith(self.baseUUID):
            item = item.split('-', 1)[0]
            item = item.lstrip('0')

        if item in self._services:
            return self._services[item].split('.')[-1]
        return 'Unknown Service: {i}'.format(i=orig_item)

    def get_uuid(self, item_name):
        if item_name not in self._services_rev:
            raise Exception('Unknown service name')
        short = self._services_rev[item_name]
        medium = '0' * (8 - len(short)) + short
        long = medium + self.baseUUID
        return long


ServicesTypes = _ServicesTypes()


class _Service(ToDictMixin):
    def __init__(self, service_type: str, iid: int):
        self.type = service_type
        self.iid = iid
        self.characteristics = []
        pass


class AcessoryInformationService(_Service):
    """
    Defined on page 216
    """

    def __init__(self, name):
        _Service.__init__(self, ServicesTypes.get_uuid('public.hap.service.accessory-information'), get_id())
        self.characteristics.append(IdentifyCharacteristic(get_id()))
        self.characteristics.append(ManufacturerCharacteristic(get_id(), 'lusiardi.de'))
        self.characteristics.append(ModelCharacteristic(get_id(), 'python bridge'))
        self.characteristics.append(NameCharacteristic(get_id(), name))
        self.characteristics.append(SerialNumberCharacteristic(get_id(), '1'))
        self.characteristics.append(FirmwareRevisionCharacteristic(get_id(), '0.1'))

    def get_name(self):
        for characteristic in self.characteristics:
            if isinstance(characteristic, NameCharacteristic):
                return characteristic.value
        return None


class _OnCharacteristis(object):
    def set_on_set_callback(self, callback):
        self._onCharacteristic.set_set_value_callback(callback)

    def set_on_get_callback(self, callback):
        self._onCharacteristic.set_get_value_callback(callback)


class FanService(_Service, _OnCharacteristis):
    """
    Defined on page 216
    """

    def __init__(self):
        _Service.__init__(self, ServicesTypes.get_uuid('public.hap.service.fan'), get_id())
        self._onCharacteristic = OnCharacteristic(get_id())
        self.characteristics.append(self._onCharacteristic)


class LightBulbService(_Service, _OnCharacteristis):
    """
    Defined on page 217
    """

    def __init__(self):
        _Service.__init__(self, ServicesTypes.get_uuid('public.hap.service.lightbulb'), get_id())
        self._onCharacteristic = OnCharacteristic(get_id())
        self.characteristics.append(self._onCharacteristic)


class OutletService(_Service, _OnCharacteristis):
    """
    Defined on page 219
    """

    def __init__(self):
        _Service.__init__(self, ServicesTypes.get_uuid('public.hap.service.outlet'), get_id())
        self._onCharacteristic = OnCharacteristic(get_id())
        self.characteristics.append(self._onCharacteristic)
        self._outletInUse = OutletInUseCharacteristic(get_id())
        self.characteristics.append(self._outletInUse)


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

