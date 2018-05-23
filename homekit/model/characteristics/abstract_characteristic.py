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
import base64
import binascii
from decimal import Decimal

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
        self.type = CharacteristicsTypes.get_uuid(characteristic_type)  # page 65, see ServicesTypes
        self.iid = iid  # page 65, unique instance id
        self.perms = [CharacteristicPermissions.paired_read]  # page 65, array of values from CharacteristicPermissions
        self.format = characteristic_format  # page 66, one of CharacteristicsTypes
        self.value = None  # page 65, required but depends on format

        self.ev = None  # boolean, not required, page 65
        self.description = None  # string, not required, page 65
        self.unit = None  # string, not required,page 66, valid values are in CharacteristicUnits
        self.minValue = None  # number, not required, page 66, used if format is int* or float
        self.maxValue = None  # number, not required, page 66, used if format is int* or float
        self.minStep = None  # number, not required, page 66, used if format is int* or float
        self.maxLen = 64  # number, not required, page 66, used if format is string
        self.maxDataLen = 2097152  # number, not required, page 66, used if format is data
        self.valid_values = None  # array, not required, see page 67, all numeric entries are allowed values
        self.valid_values_range = None  # 2 element array, not required, see page 67

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

        if self.format in [CharacteristicFormats.uint64, CharacteristicFormats.uint32, CharacteristicFormats.uint16,
                           CharacteristicFormats.uint8, CharacteristicFormats.int, CharacteristicFormats.float]:
            if self.minValue is not None and new_val < self.minValue:
                raise HomeKitStatusException(HapStatusCodes.INVALID_VALUE)
            if self.maxValue is not None and self.maxValue < new_val:
                raise HomeKitStatusException(HapStatusCodes.INVALID_VALUE)
            if self.minStep is not None:
                tmp = new_val

                # if minValue is set, the steps count from this on
                if self.minValue is not None:
                    tmp -= self.minValue

                # use Decimal to calculate the module because it has not the precision problem as float...
                if Decimal(str(tmp)) % Decimal(str(self.minStep)) != 0:
                    raise HomeKitStatusException(HapStatusCodes.INVALID_VALUE)
            if self.valid_values is not None and new_val not in self.valid_values:
                raise HomeKitStatusException(HapStatusCodes.INVALID_VALUE)
            if self.valid_values_range is not None and not (
                    self.valid_values_range[0] <= new_val <= self.valid_values_range[1]):
                raise HomeKitStatusException(HapStatusCodes.INVALID_VALUE)

        if self.format == CharacteristicFormats.data:
            try:
                byte_data = base64.decodebytes(new_val.encode())
            except binascii.Error:
                raise HomeKitStatusException(HapStatusCodes.INVALID_VALUE)
            except Exception:
                raise HomeKitStatusException(HapStatusCodes.OUT_OF_RESOURCES)
            if self.maxDataLen < len(byte_data):
                raise HomeKitStatusException(HapStatusCodes.INVALID_VALUE)

        if self.format == CharacteristicFormats.string:
            if len(new_val) > self.maxLen:
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
