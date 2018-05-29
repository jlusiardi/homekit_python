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


class OutletInUseCharacteristic(AbstractCharacteristic):
    """
    Defined on page 158
    """

    def __init__(self, iid):
        AbstractCharacteristic.__init__(self, iid, CharacteristicsTypes.OUTLET_IN_USE, CharacteristicFormats.bool)
        self.description = 'Outlet in use'
        self.perms = [CharacteristicPermissions.paired_read, CharacteristicPermissions.events]
        self.value = False


class OutletInUseCharacteristicMixin(object):
    def __init__(self, iid):
        self._outletInUse = OutletInUseCharacteristic(iid)
        self.characteristics.append(self._outletInUse)

    def set_outlet_in_use_get_callback(self, callback):
        self._outletInUse.set_get_value_callback(callback)
