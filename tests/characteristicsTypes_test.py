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

import unittest

from homekit.model.characteristics import CharacteristicsTypes


class TestCharacteristicsTypes(unittest.TestCase):

    def test_getitem_forward(self):
        self.assertEqual(CharacteristicsTypes[CharacteristicsTypes.ON], 'public.hap.characteristic.on')

    def test_getitem_reverse(self):
        self.assertEqual(CharacteristicsTypes['public.hap.characteristic.on'], CharacteristicsTypes.ON)

    def test_getitem_unknown(self):
        # self.assertEqual(CharacteristicsTypes[-99], 'Unknown Characteristic -99?')
        self.assertRaises(KeyError, CharacteristicsTypes.__getitem__, 99)

    def test_get_uuid_forward(self):
        self.assertEqual(CharacteristicsTypes.get_uuid(CharacteristicsTypes.ON),
                         '00000025-0000-1000-8000-0026BB765291')

    def test_get_uuid_reverse(self):
        self.assertEqual(CharacteristicsTypes.get_uuid('public.hap.characteristic.on'),
                         '00000025-0000-1000-8000-0026BB765291')

    def test_get_uuid_unknown(self):
        self.assertRaises(KeyError, CharacteristicsTypes.get_uuid, 'XXX')

    def test_get_short(self):
        self.assertEqual(CharacteristicsTypes.get_short(CharacteristicsTypes.ON), 'on')
        self.assertEqual(CharacteristicsTypes.get_short(CharacteristicsTypes.get_uuid(CharacteristicsTypes.ON)), 'on')
        self.assertEqual(CharacteristicsTypes.get_short(CharacteristicsTypes.DOOR_STATE_TARGET), 'door-state.target')
        self.assertEqual(CharacteristicsTypes.get_short(CharacteristicsTypes.AIR_PURIFIER_STATE_CURRENT),
                         'air-purifier.state.current')
        self.assertEqual(CharacteristicsTypes.get_short('1a'), 'lock-management.auto-secure-timeout')
