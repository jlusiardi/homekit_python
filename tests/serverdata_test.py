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
import json

from homekit.accessoryserver import AccessoryServerData
import tempfile


class TestServerData(unittest.TestCase):

    def test_example2_1_1(self):
        fp = tempfile.NamedTemporaryFile(mode='w')
        data = {
            'host_ip': '12.34.56.78',
            'host_port': 4711,
            'c#': 1,
            'category': 'bidge',
            'accessory_pin': '123-45-678',
            'accessory_pairing_id': '12:34:56:78:90:AB',
            'name': 'test007',
            'unsuccessful_tries': 0
        }
        json.dump(data, fp)
        fp.flush()

        hksd = AccessoryServerData(fp.name)
        self.assertEqual(hksd.accessory_pairing_id_bytes, b'12:34:56:78:90:AB')
        pk = bytes([0x12, 0x34])
        sk = bytes([0x56, 0x78])
        hksd.set_accessory_keys(pk, sk)
        self.assertEqual(hksd.accessory_ltpk, pk)
        self.assertEqual(hksd.accessory_ltsk, sk)
