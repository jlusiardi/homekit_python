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
from homekit.model.characteristics.name import NameCharacteristic
from homekit.model.characteristics.model import ModelCharacteristic
from homekit.model.characteristics.manufacturer import ManufacturerCharacteristic
from homekit.model.characteristics.identify import IdentifyCharacteristic
from homekit.model.characteristics.firmware_revision import FirmwareRevisionCharacteristic
from homekit.model.characteristics.serialnumber import SerialNumberCharacteristic
from homekit.model.services.service_types import ServicesTypes
from homekit.model.services.abstract_service import AbstractService


class AccessoryInformationAbstractService(AbstractService):
    """
    Defined on page 216
    """

    def __init__(self, name, manufacturer, model, serialnumber, firmwarerevision):
        AbstractService.__init__(self, ServicesTypes.get_uuid('public.hap.service.accessory-information'), get_id())
        self.characteristics.append(IdentifyCharacteristic(get_id()))
        self.characteristics.append(ManufacturerCharacteristic(get_id(), manufacturer))
        self.characteristics.append(ModelCharacteristic(get_id(), model))
        self.characteristics.append(NameCharacteristic(get_id(), name))
        self.characteristics.append(SerialNumberCharacteristic(get_id(), serialnumber))
        self.characteristics.append(FirmwareRevisionCharacteristic(get_id(), firmwarerevision))

    def get_name(self):
        for characteristic in self.characteristics:
            if isinstance(characteristic, NameCharacteristic):
                return characteristic.value
        return None
