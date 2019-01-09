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

from homekit.model.characteristics.characteristic_types import CharacteristicsTypes


class CharacteristicTypesTest(unittest.TestCase):

    def test_get_uuid_full_uuid(self):
        self.assertEqual('0000006D-0000-1000-8000-0026BB765291',
                         CharacteristicsTypes.get_uuid('0000006D-0000-1000-8000-0026BB765291'))

    def test_get_uuid_short_uuid(self):
        self.assertEqual('0000006D-0000-1000-8000-0026BB765291',
                         CharacteristicsTypes.get_uuid('6D'))

    def test_get_uuid_name(self):
        self.assertEqual('0000006D-0000-1000-8000-0026BB765291',
                         CharacteristicsTypes.get_uuid('public.hap.characteristic.position.current'))

    def test_get_uuid_unknown(self):
        self.assertRaises(KeyError, CharacteristicsTypes.get_uuid, 'UNKNOWN')

    def test_get_short_uuid_full_uuid(self):
        self.assertEqual('6D', CharacteristicsTypes.get_short_uuid('0000006D-0000-1000-8000-0026BB765291'))

    def test_get_short_uuid_name(self):
        self.assertEqual('6D', CharacteristicsTypes.get_short_uuid('public.hap.characteristic.position.current'))

    def test_get_short_uuid_short(self):
        self.assertEqual('6D', CharacteristicsTypes.get_short_uuid('6D'))

    def test_get_short_uuid_unknown(self):
        self.assertRaises(KeyError, CharacteristicsTypes.get_short_uuid, 'UNKNOWN')

    def test_get_short_uuid_passthrough(self):
        self.assertEqual('0000006D-1234-1234-1234-012345678901',
                         CharacteristicsTypes.get_short_uuid('0000006D-1234-1234-1234-012345678901'))

    def test_get_short_full_uuid(self):
        self.assertEqual('position.current', CharacteristicsTypes.get_short('0000006D-0000-1000-8000-0026BB765291'))

    def test_get_short_short_uuid(self):
        self.assertEqual('position.current', CharacteristicsTypes.get_short('6D'))

    def test_get_short_unknown(self):
        self.assertEqual('Unknown Characteristic 1234', CharacteristicsTypes.get_short('1234'))

    def test_getitem_short_uuid(self):
        self.assertEqual('public.hap.characteristic.position.current', CharacteristicsTypes['6D'])

    def test_getitem_name(self):
        self.assertEqual('6D', CharacteristicsTypes['public.hap.characteristic.position.current'])

    def test_getitem_unknown(self):
        self.assertRaises(KeyError, CharacteristicsTypes.__getitem__, 'UNKNOWN')
