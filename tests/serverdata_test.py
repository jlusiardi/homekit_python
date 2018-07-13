import unittest

from homekit.serverdata import *
import tempfile


class TestServerData(unittest.TestCase):

    def test_example2_1_1(self):
        fp = tempfile.NamedTemporaryFile(mode='w')
        data = {
            'host_ip': '12.34.56.78',
            'port': 4711,
            'accessory_pin': '123-45-678',
            'accessory_pairing_id': '12:34:56:78:90:AB',
            'name': 'test007',
            'unsuccessful_tries': 0
        }
        json.dump(data, fp)
        fp.flush()

        hksd = HomeKitServerData(fp.name)
        self.assertEqual(hksd.accessory_pairing_id_bytes, b'12:34:56:78:90:AB')
        pk = bytes([0x12, 0x34])
        sk = bytes([0x56, 0x78])
        hksd.set_accessory_keys(pk, sk)
        self.assertEqual(hksd.accessory_ltpk, pk)
        self.assertEqual(hksd.accessory_ltsk, sk)
