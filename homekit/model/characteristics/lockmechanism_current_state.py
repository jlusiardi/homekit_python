#
# Copyright 2022 Robert Schulze
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

from homekit.model.characteristics import AbstractCharacteristic, CharacteristicFormats, CharacteristicPermissions, \
    CharacteristicsTypes


class LockMechanismCurrentStateCharacteristic(AbstractCharacteristic):
    """
    Described in section 9.52
    """

    def __init__(self, iid):
        AbstractCharacteristic.__init__(self,
                                        iid,
                                        CharacteristicsTypes.LOCK_MECHANISM_CURRENT_STATE,
                                        CharacteristicFormats.uint8)
        self.perms = [CharacteristicPermissions.paired_read, CharacteristicPermissions.events]
        self.description = 'Current state of the lock mechanism'
        self.minValue = 0
        self.maxValue = 3
        self.minStep = 1
        self.value = 0


class LockMechanismCurrentStateCharacteristicMixin(object):
    def __init__(self, iid):
        self._lockMechanismCurrentStateCharacteristic = LockMechanismCurrentStateCharacteristic(iid)
        self.characteristics.append(self._lockMechanismCurrentStateCharacteristic)

    def set_lockmechanism_current_state_get_callback(self, callback):
        self._lockMechanismCurrentStateCharacteristic.set_get_value_callback(callback)
