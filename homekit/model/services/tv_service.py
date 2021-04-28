#
# Copyright 2021 Omer Nevo
# Added to homekit Copyright 2018 Joachim Lusiardi
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
from homekit.model.characteristics import ManufacturerCharacteristic, NameCharacteristic, ModelCharacteristic, SerialNumberCharacteristic, FirmwareRevisionCharacteristic, ActiveCharacteristic, ActiveIdentifierCharacteristic
from homekit.model.services import ServicesTypes, AbstractService


class TVService(AbstractService):
    def __init__(self, name, manufacturer, model, serialnumber, firmwarerevision):
        AbstractService.__init__(self, '000000D8-0000-1000-8000-0026BB765291', get_id())
        self.append_characteristic(ManufacturerCharacteristic(get_id(), manufacturer))
        self.append_characteristic(ModelCharacteristic(get_id(), model))
        self.append_characteristic(NameCharacteristic(get_id(), name))
        self.append_characteristic(SerialNumberCharacteristic(get_id(), serialnumber))
        self.append_characteristic(FirmwareRevisionCharacteristic(get_id(), firmwarerevision))
        self.append_characteristic(ActiveCharacteristic(get_id()))
        self.append_characteristic(ActiveIdentifierCharacteristic(get_id()))

    def get_name(self):
        for characteristic in self.characteristics:
            if isinstance(characteristic, NameCharacteristic):
                return characteristic.value
        return None

