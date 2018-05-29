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


class IdentifyCharacteristic(AbstractCharacteristic):
    """
    Defined on page 152
    """

    def __init__(self, iid):
        AbstractCharacteristic.__init__(self, iid, CharacteristicsTypes.IDENTIFY, CharacteristicFormats.bool)
        self.perms = [CharacteristicPermissions.paired_write]
        self.description = 'Identify'


class IdentifyCharacteristicMixin(object):
    def __init__(self, iid):
        self._identify = IdentifyCharacteristic(iid)
        self.characteristics.append(self._identify)

    def set_identify_set_callback(self, callback):
        self._identify.set_get_value_callback(callback)
