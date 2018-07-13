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

