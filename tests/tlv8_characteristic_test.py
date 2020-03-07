#
# Copyright 2020 Joachim Lusiardi
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
import tempfile
import threading
import time

import tlv8

from homekit import Controller
from homekit import AccessoryServer
from homekit.model.characteristics import CharacteristicsTypes, AbstractTlv8Characteristic, CharacteristicPermissions, \
    AbstractTlv8CharacteristicValue
from homekit.model import Accessory
from homekit.model.services import LightBulbService
from homekit.model import mixin as model_mixin
from homekit.model import get_id


class T(threading.Thread):
    def __init__(self, accessoryServer):
        threading.Thread.__init__(self)
        self.a_s = accessoryServer

    def run(self):
        self.a_s.publish_device()
        self.a_s.serve_forever()


class Tlv8CharacteristicValue(AbstractTlv8CharacteristicValue):
    def __init__(self, val):
        self.val = val

    def to_bytes(self) -> bytes:
        return tlv8.EntryList([tlv8.Entry(1, self.val)]).encode()

    @staticmethod
    def from_bytes(data: bytes):
        el = tlv8.decode(data, {1: tlv8.DataType.INTEGER})
        val = el.first_by_id(1).data
        return Tlv8CharacteristicValue(val)


class Tlv8Characteristic(AbstractTlv8Characteristic):
    def __init__(self, iid, value):
        AbstractTlv8Characteristic.__init__(self, iid, value, CharacteristicsTypes.SETUP_ENDPOINTS)
        self.maxLen = 64
        self.description = 'Name'
        self.perms = [CharacteristicPermissions.paired_read, CharacteristicPermissions.paired_write]


class TestTlvCharacteristic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_file = tempfile.NamedTemporaryFile()
        cls.config_file.write("""{
            "accessory_ltpk": "7986cf939de8986f428744e36ed72d86189bea46b4dcdc8d9d79a3e4fceb92b9",
            "accessory_ltsk": "3d99f3e959a1f93af4056966f858074b2a1fdec1c5fd84a51ea96f9fa004156a",
            "accessory_pairing_id": "12:34:56:00:01:0A",
            "accessory_pin": "031-45-154",
            "c#": 1,
            "category": "Lightbulb",
            "host_ip": "127.0.0.1",
            "host_port": 51842,
            "name": "unittestLight",
            "peers": {
                "decc6fa3-de3e-41c9-adba-ef7409821bfc": {
                    "admin": true,
                    "key": "d708df2fbf4a8779669f0ccd43f4962d6d49e4274f88b1292f822edc3bcf8ed8"
                }
            },
            "unsuccessful_tries": 0
        }""".encode())
        cls.config_file.flush()

        # Make sure get_id() numbers are stable between tests
        model_mixin.id_counter = 0

        cls.httpd = AccessoryServer(cls.config_file.name, None)
        accessory = Accessory('Testlicht', 'lusiardi.de', 'Demoserver', '0001', '0.1')
        lightBulbService = LightBulbService()
        cls.tlvChar = Tlv8Characteristic(get_id(), Tlv8CharacteristicValue(0))
        lightBulbService.append_characteristic(cls.tlvChar)
        accessory.services.append(lightBulbService)
        cls.httpd.add_accessory(accessory)
        t = T(cls.httpd)
        t.start()
        time.sleep(5)
        cls.controller_file = tempfile.NamedTemporaryFile()
        cls.controller_file.write("""{
            "alias": {
                "Connection": "IP",
                "iOSDeviceLTPK": "d708df2fbf4a8779669f0ccd43f4962d6d49e4274f88b1292f822edc3bcf8ed8",
                "iOSPairingId": "decc6fa3-de3e-41c9-adba-ef7409821bfc",
                "AccessoryLTPK": "7986cf939de8986f428744e36ed72d86189bea46b4dcdc8d9d79a3e4fceb92b9",
                "AccessoryPairingID": "12:34:56:00:01:0A",
                "AccessoryPort": 51842,
                "AccessoryIP": "127.0.0.1",
                "iOSDeviceLTSK": "fa45f082ef87efc6c8c8d043d74084a3ea923a2253e323a7eb9917b4090c2fcc"
            }
        }""".encode())
        cls.controller_file.flush()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.unpublish_device()
        cls.httpd.shutdown()
        cls.config_file.close()

    def setUp(self):
        self.controller = Controller()

    def tearDown(self):
        self.controller.shutdown()

    def test_get_accessories(self):
        self.controller.load_data(self.controller_file.name)
        pairing = self.controller.get_pairings()['alias']
        result = pairing.list_accessories_and_characteristics()
        for characteristic in result[0]['services'][0]['characteristics']:
            if characteristic['iid'] == self.__class__.tlvChar.iid:
                self.assertIn('value', characteristic)
                self.assertEqual('AQEA', characteristic['value'])
                self.assertIn('format', characteristic)
                self.assertEqual('tlv8', characteristic['format'])

    def test_get_characteristic(self):
        self.controller.load_data(self.controller_file.name)
        pairing = self.controller.get_pairings()['alias']

        self.__class__.tlvChar.value.val = 420023
        result = pairing.get_characteristics([(1, 11)])
        self.assertIn((1, 11), result)
        self.assertIn('value', result[(1, 11)])
        self.assertEqual('AQS3aAYA', result[(1, 11)]['value'])
        self.assertEqual(['value'], list(result[(1, 11)].keys()))

        self.__class__.tlvChar.value.val = 230042
        result = pairing.get_characteristics([(1, 11)])
        self.assertIn((1, 11), result)
        self.assertIn('value', result[(1, 11)])
        self.assertEqual('AQSaggMA', result[(1, 11)]['value'])
        self.assertEqual(['value'], list(result[(1, 11)].keys()))

    def test_get_characteristic_with_getter(self):
        self.controller.load_data(self.controller_file.name)
        pairing = self.controller.get_pairings()['alias']

        def get():
            return Tlv8CharacteristicValue(123)

        self.__class__.tlvChar.set_get_value_callback(get)
        result = pairing.get_characteristics([(1, 11)])
        self.__class__.tlvChar.set_get_value_callback(None)
        self.assertIn((1, 11), result)
        self.assertIn('value', result[(1, 11)])
        self.assertEqual('AQF7', result[(1, 11)]['value'])
        self.assertEqual(['value'], list(result[(1, 11)].keys()))

    def test_put_characteristic(self):
        """"""
        self.controller.load_data(self.controller_file.name)
        pairing = self.controller.get_pairings()['alias']

        result = pairing.put_characteristics([(1, 11, 'AQS3aAYA')])
        self.assertEqual(result, {})
        self.assertEqual(self.__class__.tlvChar.value.val, 420023)

    def test_put_characteristic_with_setter(self):
        """"""
        self.controller.load_data(self.controller_file.name)
        pairing = self.controller.get_pairings()['alias']

        def set(val):
            self.assertEqual(val.val, 420023)

        self.__class__.tlvChar.set_set_value_callback(set)
        result = pairing.put_characteristics([(1, 11, 'AQS3aAYA')])
        self.__class__.tlvChar.set_set_value_callback(None)
        self.assertEqual(result, {})
        self.assertEqual(self.__class__.tlvChar.value.val, 420023)
