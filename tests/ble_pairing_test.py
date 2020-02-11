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
import tlv8

from homekit.exceptions import FormatError
from homekit.protocol.tlv import TLV

from homekit.tools import BLE_TRANSPORT_SUPPORTED

if BLE_TRANSPORT_SUPPORTED:
    from homekit.controller.ble_impl import BlePairing


@unittest.skipIf(not BLE_TRANSPORT_SUPPORTED, 'BLE no supported')
class TestBLEPairing(unittest.TestCase):
    def _create_pairing_data(self):
        return {
            'accessories': [
                {
                    'aid': 1,
                    'services': [
                        {
                            'characteristics': [
                                {
                                    'iid': 2,
                                    'format': 'bool'
                                },
                                {
                                    'iid': 3,
                                    'format': 'int'
                                },
                                {
                                    'iid': 4,
                                    'format': 'float'
                                },
                                {
                                    'iid': 5,
                                    'format': 'uint8'
                                },
                                {
                                    'iid': 6,
                                    'format': 'uint16'
                                },
                                {
                                    'iid': 7,
                                    'format': 'uint32'
                                },
                                {
                                    'iid': 8,
                                    'format': 'uint64'
                                },
                                {
                                    'iid': 9,
                                    'format': 'string'
                                },
                                {
                                    'iid': 10,
                                    'format': 'tlv'
                                }
                            ]
                        }
                    ]
                }
            ]
        }

    def test__convert_from_python__bool__wrong_values(self):
        pairing_data = self._create_pairing_data()
        pairing = BlePairing(pairing_data)
        self.assertRaises(FormatError, pairing._convert_from_python, 1, 2, 123)

    def test__convert_from_python__bool__proper_values(self):
        pairing_data = self._create_pairing_data()
        pairing = BlePairing(pairing_data)
        result = pairing._convert_from_python(1, 2, True)
        self.assertEqual(b'\x01', result)
        result = pairing._convert_from_python(1, 2, False)
        self.assertEqual(b'\x00', result)

    def test__convert_from_python__int__wrong_values(self):
        pairing_data = self._create_pairing_data()
        pairing = BlePairing(pairing_data)
        self.assertRaises(FormatError, pairing._convert_from_python, 1, 3, 'hallo')
        self.assertRaises(FormatError, pairing._convert_from_python, 1, 3, 12.3)

    def test__convert_from_python__int__proper_values(self):
        pairing_data = self._create_pairing_data()
        pairing = BlePairing(pairing_data)
        result = pairing._convert_from_python(1, 3, 1234)
        self.assertEqual(b'\xd2\x04\x00\x00', result)

    def test__convert_from_python__float__wrong_values(self):
        pairing_data = self._create_pairing_data()
        pairing = BlePairing(pairing_data)
        self.assertRaises(FormatError, pairing._convert_from_python, 1, 4, 'hallo')
        self.assertRaises(FormatError, pairing._convert_from_python, 1, 4, True)

    def test__convert_from_python__float__proper_values(self):
        pairing_data = self._create_pairing_data()
        pairing = BlePairing(pairing_data)
        result = pairing._convert_from_python(1, 4, 3.141)
        self.assertEqual(b'\x25\x06\x49\x40', result)

    def test__convert_from_python__uint8__wrong_values(self):
        pairing_data = self._create_pairing_data()
        pairing = BlePairing(pairing_data)
        self.assertRaises(FormatError, pairing._convert_from_python, 1, 5, 'hallo')
        self.assertRaises(FormatError, pairing._convert_from_python, 1, 5, True)
        self.assertRaises(FormatError, pairing._convert_from_python, 1, 5, 160000)
        self.assertRaises(FormatError, pairing._convert_from_python, 1, 5, 2.53)
        self.assertRaises(FormatError, pairing._convert_from_python, 1, 5, -1)

    def test__convert_from_python__uint8__proper_values(self):
        pairing_data = self._create_pairing_data()
        pairing = BlePairing(pairing_data)
        result = pairing._convert_from_python(1, 5, 42)
        self.assertEqual(b'\x2A', result)

    def test__convert_from_python__uint16__wrong_values(self):
        pairing_data = self._create_pairing_data()
        pairing = BlePairing(pairing_data)
        self.assertRaises(FormatError, pairing._convert_from_python, 1, 6, 'hallo')
        self.assertRaises(FormatError, pairing._convert_from_python, 1, 6, True)
        self.assertRaises(FormatError, pairing._convert_from_python, 1, 6, 160000)
        self.assertRaises(FormatError, pairing._convert_from_python, 1, 6, 2.53)
        self.assertRaises(FormatError, pairing._convert_from_python, 1, 6, -1)

    def test__convert_from_python__uint16__proper_values(self):
        pairing_data = self._create_pairing_data()
        pairing = BlePairing(pairing_data)
        result = pairing._convert_from_python(1, 6, 42)
        self.assertEqual(b'\x2A\x00', result)

    def test__convert_from_python__uint32__wrong_values(self):
        pairing_data = self._create_pairing_data()
        pairing = BlePairing(pairing_data)
        self.assertRaises(FormatError, pairing._convert_from_python, 1, 7, 'hallo')
        self.assertRaises(FormatError, pairing._convert_from_python, 1, 7, True)
        self.assertRaises(FormatError, pairing._convert_from_python, 1, 7, 1600000000000)
        self.assertRaises(FormatError, pairing._convert_from_python, 1, 7, 2.53)
        self.assertRaises(FormatError, pairing._convert_from_python, 1, 7, -1)

    def test__convert_from_python__uint32__proper_values(self):
        pairing_data = self._create_pairing_data()
        pairing = BlePairing(pairing_data)
        result = pairing._convert_from_python(1, 7, 42)
        self.assertEqual(b'\x2A\x00\x00\x00', result)

    def test__convert_from_python__uint64__wrong_values(self):
        pairing_data = self._create_pairing_data()
        pairing = BlePairing(pairing_data)
        self.assertRaises(FormatError, pairing._convert_from_python, 1, 8, 'hallo')
        self.assertRaises(FormatError, pairing._convert_from_python, 1, 8, True)
        self.assertRaises(FormatError, pairing._convert_from_python, 1, 8, 10E20)
        self.assertRaises(FormatError, pairing._convert_from_python, 1, 8, 2.53)
        self.assertRaises(FormatError, pairing._convert_from_python, 1, 8, -1)

    def test__convert_from_python__uint64__proper_values(self):
        pairing_data = self._create_pairing_data()
        pairing = BlePairing(pairing_data)
        result = pairing._convert_from_python(1, 8, 42)
        self.assertEqual(b'\x2A\x00\x00\x00\x00\x00\x00\x00', result)

    def test__convert_from_python__string__wrong_values(self):
        pairing_data = self._create_pairing_data()
        pairing = BlePairing(pairing_data)
        self.assertRaises(FormatError, pairing._convert_from_python, 1, 9, 2)
        self.assertRaises(FormatError, pairing._convert_from_python, 1, 9, True)
        self.assertRaises(FormatError, pairing._convert_from_python, 1, 9, 10E20)
        self.assertRaises(FormatError, pairing._convert_from_python, 1, 9, 2.53)
        self.assertRaises(FormatError, pairing._convert_from_python, 1, 9, -1)

    def test__convert_from_python__string__proper_values(self):
        pairing_data = self._create_pairing_data()
        pairing = BlePairing(pairing_data)
        self.assertEqual(b'Hello', pairing._convert_from_python(1, 9, 'Hello'))

    def test__convert_from_python__tlv__proper_values(self):
        pairing_data = self._create_pairing_data()
        pairing = BlePairing(pairing_data)
        data = tlv8.encode([
            tlv8.Entry(6, b'\x03')
        ])
        self.assertEqual(b'\x06\x01\x03', pairing._convert_from_python(1, 10, data))

    def test__find_characteristic_in_pairing_data__found(self):
        pairing_data = self._create_pairing_data()
        pairing = BlePairing(pairing_data)
        result = pairing._find_characteristic_in_pairing_data(1, 2)
        self.assertIsNotNone(result)
        self.assertIn('format', result)
        self.assertEqual('bool', result['format'])

    def test__find_characteristic_in_pairing_data__not_found(self):
        pairing_data = self._create_pairing_data()
        pairing = BlePairing(pairing_data)
        result = pairing._find_characteristic_in_pairing_data(1, 1)
        self.assertIsNone(result)
