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
from homekit.model.characteristics import NameCharacteristic, ModelCharacteristic, ManufacturerCharacteristic, \
    IdentifyCharacteristic, FirmwareRevisionCharacteristic, SerialNumberCharacteristic
from homekit.model.services import ServicesTypes, AbstractService


class AccessoryInformationService(AbstractService):
    """
    Defined on page 216
    """

    def __init__(self, name, manufacturer, model, serialnumber, firmwarerevision):
        AbstractService.__init__(self, ServicesTypes.get_uuid('public.hap.service.accessory-information'), get_id())
        self.append_characteristic(IdentifyCharacteristic(get_id()))
        self.append_characteristic(ManufacturerCharacteristic(get_id(), manufacturer))
        self.append_characteristic(ModelCharacteristic(get_id(), model))
        self.append_characteristic(NameCharacteristic(get_id(), name))
        self.append_characteristic(SerialNumberCharacteristic(get_id(), serialnumber))
        self.append_characteristic(FirmwareRevisionCharacteristic(get_id(), firmwarerevision))

    def get_name(self):
        for characteristic in self.characteristics:
            if isinstance(characteristic, NameCharacteristic):
                return characteristic.value
        return None
