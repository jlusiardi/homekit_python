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


class MicrophoneMuteCharacteristic(AbstractCharacteristic):
    """
    Defined on page 157
    """

    def __init__(self, iid):
        AbstractCharacteristic.__init__(self, iid, CharacteristicsTypes.MUTE, CharacteristicFormats.bool)
        self.description = 'Mute microphone (on/off)'
        self.perms = [CharacteristicPermissions.paired_write, CharacteristicPermissions.paired_read,
                      CharacteristicPermissions.events]
        self.value = False


class MicrophoneMuteCharacteristicMixin(object):
    def __init__(self, iid):
        self._muteCharacteristic = MicrophoneMuteCharacteristic(iid)
        self.characteristics.append(self._muteCharacteristic)

    def set_mute_set_callback(self, callback):
        self._muteCharacteristic.set_set_value_callback(callback)

    def set_mute_get_callback(self, callback):
        self._muteCharacteristic.set_get_value_callback(callback)
