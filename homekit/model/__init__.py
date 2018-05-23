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

from homekit.model.mixin import ToDictMixin, get_id
from homekit.model.services import AccessoryInformationAbstractService, LightBulbService, FanService, \
    BHSLightBulbService
from homekit.model.categories import Categories


class Accessory(ToDictMixin):
    def __init__(self, name, manufacturer, model, serial_number, firmware_revision):
        self.aid = get_id()
        self.services = [
            AccessoryInformationAbstractService(name, manufacturer, model, serial_number, firmware_revision)
        ]

    def get_name(self):
        for service in self.services:
            if isinstance(service, AccessoryInformationAbstractService):
                return service.get_name()
        return None


class Accessories(ToDictMixin):
    def __init__(self):
        self.accessories = []

    def add_accessory(self, accessory: Accessory):
        self.accessories.append(accessory)
