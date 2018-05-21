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

from distutils.util import strtobool

from homekit.model.mixin import ToDictMixin
from homekit.model.characteristics.characteristic_types import CharacteristicsTypes
from homekit.model.characteristics.characteristic_formats import CharacteristicFormats
from homekit.model.characteristics.characteristic_permissions import CharacteristicPermissions
from homekit.statuscodes import HapStatusCodes
from homekit.exception import HomeKitStatusException


class AbstractCharacteristic(ToDictMixin):
    def __init__(self, iid: int, characteristic_type: str, characteristic_format: str):
        if type(self) is AbstractCharacteristic:
            raise Exception('AbstractCharacteristic is an abstract class and cannot be instantiated directly')
        self.type = CharacteristicsTypes.get_uuid(characteristic_type)
        self.iid = iid
        self.perms = [CharacteristicPermissions.paired_read]
        self.format = characteristic_format
        self.value = None
        self.ev = None  # not required
        self.description = None  # string, not required
        self.unit = None  # string, not required
        self.minValue = None  # number, not required
        self.maxValue = None  # number, not required
        self.minStep = None  # number, not required
        self.maxLen = None  # number, not required
        self.maxDataLen = None  # number, not required
        self.valid_values = None  # array, not required
        self.valid_values_range = None  # array, not required
        self._set_value_callback = None
        self._get_value_callback = None

    def set_set_value_callback(self, callback):
        self._set_value_callback = callback

    def set_get_value_callback(self, callback):
        self._get_value_callback = callback

    def set_events(self, new_val):
        self.ev = new_val

    def set_value(self, new_val):
        if CharacteristicPermissions.paired_write not in self.perms:
            raise HomeKitStatusException(HapStatusCodes.CANT_READ_WRITE_ONLY)
        try:
            # convert input to python int if it is any kind of int
            if self.format in [CharacteristicFormats.uint64, CharacteristicFormats.uint32, CharacteristicFormats.uint16,
                               CharacteristicFormats.uint8, CharacteristicFormats.int]:
                new_val = int(new_val)
            # convert input to python float
            if self.format == CharacteristicFormats.float:
                new_val = float(new_val)
            # convert to python bool
            if self.format == CharacteristicFormats.bool:
                new_val = strtobool(str(new_val))
        except ValueError:
            raise HomeKitStatusException(HapStatusCodes.INVALID_VALUE)
        self.value = new_val
        if self._set_value_callback:
            self._set_value_callback(new_val)

    def get_value(self):
        if CharacteristicPermissions.paired_read not in self.perms:
            raise HomeKitStatusException(HapStatusCodes.CANT_READ_WRITE_ONLY)
        if self._get_value_callback:
            return self._get_value_callback()
        return self.value
