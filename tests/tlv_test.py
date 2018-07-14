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

from homekit.tlv import TLV


class TestTLV(unittest.TestCase):

    def test_example1(self):
        example_1 = bytearray.fromhex('060103010568656c6c6f')
        dict_1_1 = TLV.decode_bytearray(example_1)

        bytearray_1 = TLV.encode_dict(dict_1_1)
        dict_1_2 = TLV.decode_bytearray(bytearray_1)
        self.assertEqual(dict_1_1, dict_1_2)

    def test_example2(self):
        example_2 = bytearray.fromhex('060103' + ('09FF' + 255 * '61' + '092D' + 45 * '61') + '010568656c6c6f')
        dict_2_1 = TLV.decode_bytearray(example_2)

        bytearray_2 = TLV.encode_dict(dict_2_1)
        dict_2_2 = TLV.decode_bytearray(bytearray_2)
        self.assertEqual(dict_2_1, dict_2_2)

