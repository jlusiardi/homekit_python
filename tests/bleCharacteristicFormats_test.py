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

from homekit.model.characteristics.characteristic_formats import BleCharacteristicFormats


class BleCharacteristicFormatsTest(unittest.TestCase):

    def test_get_unknown_key(self):
        self.assertEqual('unknown', BleCharacteristicFormats.get(-0xC0FFEE, 'unknown'))

    def test_get_known_key(self):
        self.assertEqual('bool', BleCharacteristicFormats.get(1, 'unknown'))
