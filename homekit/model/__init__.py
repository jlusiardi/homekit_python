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

__all__ = [
    'AccessoryInformationService', 'BHSLightBulbService', 'FanService', 'LightBulbService', 'ThermostatService',
    'Categories', 'CharacteristicPermissions', 'CharacteristicFormats', 'FeatureFlags', 'Accessory'
]

import json
from homekit.model.mixin import ToDictMixin, get_id
from homekit.model.services import AccessoryInformationService, LightBulbService, FanService, \
    BHSLightBulbService, ThermostatService
from homekit.model.categories import Categories
from homekit.model.characteristics import CharacteristicPermissions, CharacteristicFormats
from homekit.model.feature_flags import FeatureFlags
from homekit.model.characteristics import IdentifyCharacteristic


class Accessory(ToDictMixin):
    def __init__(self, name, manufacturer, model, serial_number, firmware_revision):
        self.aid = get_id()
        self.services = [
            AccessoryInformationService(name, manufacturer, model, serial_number, firmware_revision)
        ]

    def add_service(self, service):
        self.services.append(service)

    def set_identify_callback(self, func):
        """
        Set the callback function for this accessory. This function will be called on paired calls to identify.

        :param func: a function without any parameters and without return type.
        """

        def tmp(x):
            func()

        for service in self.services:
            if isinstance(service, AccessoryInformationService):
                for characteristic in service.characteristics:
                    if isinstance(characteristic, IdentifyCharacteristic):
                        characteristic.set_set_value_callback(tmp)

    def to_accessory_and_service_list(self):
        services_list = []
        for s in self.services:
            services_list.append(s.to_accessory_and_service_list())
        d = {
            'aid': self.aid,
            'services': services_list
        }
        return d


class Accessories(ToDictMixin):
    def __init__(self):
        self.accessories = []

    def add_accessory(self, accessory: Accessory):
        self.accessories.append(accessory)

    def to_accessory_and_service_list(self):
        accessories_list = []
        for a in self.accessories:
            accessories_list.append(a.to_accessory_and_service_list())
        d = {'accessories': accessories_list}
        return json.dumps(d)
