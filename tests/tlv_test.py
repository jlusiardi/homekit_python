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

from homekit.protocol.tlv import TLV, TlvParseException


class TestTLV(unittest.TestCase):

    def test_long_values_1(self):
        val = [
            [TLV.kTLVType_State, TLV.M3],
            [TLV.kTLVType_Certificate, (300 * 'a').encode()],
            [TLV.kTLVType_Identifier, 'hello'.encode()],
        ]
        res = TLV.decode_bytearray(TLV.encode_list(val))
        self.assertEqual(val, res)

    def test_long_values_2(self):
        val = [
            [TLV.kTLVType_State, TLV.M3],
            [TLV.kTLVType_Certificate, (150 * 'a' + 150 * 'b').encode()],
            [TLV.kTLVType_Identifier, 'hello'.encode()],
        ]
        res = TLV.decode_bytearray(TLV.encode_list(val))
        self.assertEqual(val, res)

    def test_long_values_decode_bytearray_to_list(self):
        example = bytearray.fromhex('060103' + ('09FF' + 255 * '61' + '092D' + 45 * '61') + '010568656c6c6f')
        expected = [
            [6, bytearray(b'\x03')],
            [9, bytearray(300 * b'a')],
            [1, bytearray(b'hello')]
        ]

        data = TLV.decode_bytearray(example)
        self.assertListEqual(data, expected)

    def test_long_values_decode_bytes_to_list(self):
        example = bytes(bytearray.fromhex('060103' + ('09FF' + 255 * '61' + '092D' + 45 * '61') + '010568656c6c6f'))
        expected = [
            [6, bytearray(b'\x03')],
            [9, bytearray(300 * b'a')],
            [1, bytearray(b'hello')]
        ]

        data = TLV.decode_bytes(example)
        self.assertListEqual(data, expected)

    # def test_long_values_decode_bytearray(self):
    #     example = bytearray.fromhex('060103' + ('09FF' + 255 * '61' + '092D' + 45 * '61') + '010568656c6c6f')
    #     expected = {
    #         6: bytearray(b'\x03'),
    #         9: bytearray(300 * b'a'),
    #         1: bytearray(b'hello')
    #     }
    #
    #     data = TLV.decode_bytearray(example)
    #     self.assertDictEqual(data, expected)
    #
    # def test_decode_bytearray_not_enough_data(self):
    #     example = bytearray.fromhex('060103' + '09FF' + 25 * '61')  # should have been 255 '61'
    #     self.assertRaises(TlvParseException, TLV.decode_bytearray, example)

    def test_decode_bytearray_to_list_not_enough_data(self):
        example = bytearray.fromhex('060103' + '09FF' + 25 * '61')  # should have been 255 '61'
        self.assertRaises(TlvParseException, TLV.decode_bytearray, example)

    def test_decode_bytes_to_list_not_enough_data(self):
        example = bytes(bytearray.fromhex('060103' + '09FF' + 25 * '61'))  # should have been 255 '61'
        self.assertRaises(TlvParseException, TLV.decode_bytes, example)

    def test_encode_list_key_error(self):
        example = [(-1, 'hello',), ]
        self.assertRaises(ValueError, TLV.encode_list, example)
        example = [(256, 'hello',), ]
        self.assertRaises(ValueError, TLV.encode_list, example)
        example = [('test', 'hello',), ]
        self.assertRaises(ValueError, TLV.encode_list, example)

    def test_to_string_for_list(self):
        example = [(1, 'hello',), ]
        res = TLV.to_string(example)
        self.assertEqual(res, '[\n  1: (5 bytes/<class \'str\'>) hello\n]\n')
        example = [(1, 'hello',), (2, 'world',), ]
        res = TLV.to_string(example)
        self.assertEqual(res, '[\n  1: (5 bytes/<class \'str\'>) hello\n  2: (5 bytes/<class \'str\'>) world\n]\n')

    def test_to_string_for_dict(self):
        example = {1: 'hello'}
        res = TLV.to_string(example)
        self.assertEqual(res, '{\n  1: (5 bytes/<class \'str\'>) hello\n}\n')
        example = {1: 'hello', 2: 'world'}
        res = TLV.to_string(example)
        self.assertEqual(res, '{\n  1: (5 bytes/<class \'str\'>) hello\n  2: (5 bytes/<class \'str\'>) world\n}\n')

    def test_to_string_for_dict_bytearray(self):
        example = {1: bytearray([0x42, 0x23])}
        res = TLV.to_string(example)
        self.assertEqual(res, '{\n  1: (2 bytes/<class \'bytearray\'>) 0x4223\n}\n')

    def test_to_string_for_list_bytearray(self):
        example = [[1, bytearray([0x42, 0x23])]]
        res = TLV.to_string(example)
        self.assertEqual(res, '[\n  1: (2 bytes/<class \'bytearray\'>) 0x4223\n]\n')

    def test_separator_list(self):
        val = [
            [TLV.kTLVType_State, TLV.M3],
            TLV.kTLVType_Separator_Pair,
            [TLV.kTLVType_State, TLV.M4],
        ]
        res = TLV.decode_bytearray(TLV.encode_list(val))
        self.assertEqual(val, res)

    def test_separator_list_error(self):
        val = [
            [TLV.kTLVType_State, TLV.M3],
            [TLV.kTLVType_Separator, 'test'],
            [TLV.kTLVType_State, TLV.M4],
        ]
        self.assertRaises(ValueError, TLV.encode_list, val)

    def test_reorder_1(self):
        val = [
            [TLV.kTLVType_State, TLV.M3],
            [TLV.kTLVType_Salt, (16 * 'a').encode()],
            [TLV.kTLVType_PublicKey, (384 * 'b').encode()],
        ]
        tmp = TLV.reorder(val, [TLV.kTLVType_State, TLV.kTLVType_PublicKey, TLV.kTLVType_Salt])
        self.assertEqual(tmp[0][0], TLV.kTLVType_State)
        self.assertEqual(tmp[0][1], TLV.M3)
        self.assertEqual(tmp[1][0], TLV.kTLVType_PublicKey)
        self.assertEqual(tmp[1][1], (384 * 'b').encode())
        self.assertEqual(tmp[2][0], TLV.kTLVType_Salt)
        self.assertEqual(tmp[2][1], (16 * 'a').encode())

    def test_reorder_2(self):
        val = [
            [TLV.kTLVType_State, TLV.M3],
            [TLV.kTLVType_Salt, (16 * 'a').encode()],
            [TLV.kTLVType_PublicKey, (384 * 'b').encode()],
        ]
        tmp = TLV.reorder(val, [TLV.kTLVType_State, TLV.kTLVType_Salt])
        self.assertEqual(tmp[0][0], TLV.kTLVType_State)
        self.assertEqual(tmp[0][1], TLV.M3)
        self.assertEqual(tmp[1][0], TLV.kTLVType_Salt)
        self.assertEqual(tmp[1][1], (16 * 'a').encode())

    def test_reorder_3(self):
        val = [
            [TLV.kTLVType_State, TLV.M3],
            [TLV.kTLVType_Salt, (16 * 'a').encode()],
            [TLV.kTLVType_PublicKey, (384 * 'b').encode()],
        ]
        tmp = TLV.reorder(val, [TLV.kTLVType_State, TLV.kTLVType_Error, TLV.kTLVType_Salt])
        self.assertEqual(tmp[0][0], TLV.kTLVType_State)
        self.assertEqual(tmp[0][1], TLV.M3)
        self.assertEqual(tmp[1][0], TLV.kTLVType_Salt)
        self.assertEqual(tmp[1][1], (16 * 'a').encode())

    def test_filter(self):
        example = bytes(bytearray.fromhex('060103' + '010203'))
        expected = [
            [6, bytearray(b'\x03')],
        ]

        data = TLV.decode_bytes(example, expected=[6])
        self.assertListEqual(data, expected)
