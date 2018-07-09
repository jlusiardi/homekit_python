import unittest

from homekit.protocol.tlv import TLV


class TestTlvMethods(unittest.TestCase):

    def test_long_values_1(self):
        val = [
            [TLV.kTLVType_State, TLV.M3],
            [TLV.kTLVType_Certificate, (300*'a').encode()],
            [TLV.kTLVType_Identifier, 'hello'.encode()],
        ]
        res = TLV.decode_bytearray_to_list(TLV.encode_list(val))
        self.assertEqual(val, res)
        pass

    def test_long_values_2(self):
        val = [
            [TLV.kTLVType_State, TLV.M3],
            [TLV.kTLVType_Certificate, (150*'a'+150*'b').encode()],
            [TLV.kTLVType_Identifier, 'hello'.encode()],
        ]
        res = TLV.decode_bytearray_to_list(TLV.encode_list(val))
        self.assertEqual(val, res)
        pass

