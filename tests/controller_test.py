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
import tempfile
import threading
import time

from homekit import Controller
from homekit import AccessoryServer
from homekit.exceptions import AccessoryNotFoundError, AlreadyPairedError, UnavailableError, FormatError
from homekit.model import Accessory
from homekit.model.services import LightBulbService


class T(threading.Thread):
    def __init__(self, accessoryServer):
        threading.Thread.__init__(self)
        self.a_s = accessoryServer

    def run(self):
        self.a_s.publish_device()
        self.a_s.serve_forever()


value = 0
identify = 0


def identify_callback():
    global identify
    identify = 1


def set_value(new_value):
    global value
    value = new_value


class TestControllerUnpaired(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # prepare config file for unpaired accessory server
        cls.config_file = tempfile.NamedTemporaryFile()
        cls.config_file.write("""{
              "accessory_ltpk": "7986cf939de8986f428744e36ed72d86189bea46b4dcdc8d9d79a3e4fceb92b9",
              "accessory_ltsk": "3d99f3e959a1f93af4056966f858074b2a1fdec1c5fd84a51ea96f9fa004156a",
              "accessory_pairing_id": "12:34:56:00:01:0B",
              "accessory_pin": "010-22-020",
              "c#": 0,
              "category": "Lightbulb",
              "host_ip": "127.0.0.1",
              "host_port": 54321,
              "name": "unittestLight",
              "peers": {
              },
              "unsuccessful_tries": 0
            }""".encode())
        cls.config_file.flush()

        cls.httpd = AccessoryServer(cls.config_file.name, None)
        cls.httpd.set_identify_callback(identify_callback)
        accessory = Accessory('Testlicht', 'lusiardi.de', 'Demoserver', '0001', '0.1')
        accessory.set_identify_callback(identify_callback)
        lightBulbService = LightBulbService()
        lightBulbService.set_on_set_callback(set_value)
        accessory.services.append(lightBulbService)
        cls.httpd.add_accessory(accessory)
        t = T(cls.httpd)
        t.start()
        time.sleep(10)
        cls.controller_file = tempfile.NamedTemporaryFile()

    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self, methodName)
        self.controller_file = tempfile.NamedTemporaryFile()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.unpublish_device()
        cls.httpd.shutdown()
        cls.config_file.close()

    def setUp(self):
        self.controller = Controller()

    def test_01_1_discover(self):
        """Try to discover the test accessory"""
        result = self.controller.discover()
        found = False
        for device in result:
            if '12:34:56:00:01:0B' == device['id']:
                found = True
        self.assertTrue(found)

    def test_01_2_unpaired_identify(self):
        """Try to trigger the identification of the test accessory"""
        global identify
        self.controller.identify('12:34:56:00:01:0B')
        self.assertEqual(1, identify)
        identify = 0

    def test_01_3_unpaired_identify_not_found(self):
        """Try to identify a non existing accessory. This should result in AccessoryNotFoundError"""
        self.assertRaises(AccessoryNotFoundError, self.controller.identify, '12:34:56:00:01:0C')

    def test_02_pair(self):
        """Try to pair the test accessory"""
        self.controller.perform_pairing('alias', '12:34:56:00:01:0B', '010-22-020')
        pairings = self.controller.get_pairings()
        self.controller.save_data(TestControllerUnpaired.controller_file.name)
        self.assertIn('alias', pairings)

    def test_02_pair_accessory_not_found(self):
        """"""
        self.assertRaises(AccessoryNotFoundError, self.controller.perform_pairing, 'alias1', '12:34:56:00:01:1B',
                          '010-22-020')

    def test_02_pair_wrong_pin(self):
        """"""
        self.assertRaises(UnavailableError, self.controller.perform_pairing, 'alias2', '12:34:56:00:01:0B',
                          '010-22-021')


class TestControllerPaired(unittest.TestCase):
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

        cls.httpd = AccessoryServer(cls.config_file.name, None)
        cls.httpd.set_identify_callback(identify_callback)
        accessory = Accessory('Testlicht', 'lusiardi.de', 'Demoserver', '0001', '0.1')
        accessory.set_identify_callback(identify_callback)
        lightBulbService = LightBulbService()
        lightBulbService.set_on_set_callback(set_value)
        accessory.services.append(lightBulbService)
        cls.httpd.add_accessory(accessory)
        t = T(cls.httpd)
        t.start()
        time.sleep(5)
        cls.controller_file = tempfile.NamedTemporaryFile()
        cls.controller_file.write("""{
            "alias": {
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

    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self, methodName)

    @classmethod
    def tearDownClass(cls):
        cls.httpd.unpublish_device()
        cls.httpd.shutdown()
        cls.config_file.close()

    def setUp(self):
        self.controller = Controller()

    def tearDown(self):
        self.controller.shutdown()

    def test_01_1_discover(self):
        result = self.controller.discover(5)
        found = None
        for device in result:
            if '12:34:56:00:01:0A' == device['id']:
                found = device
        self.assertIsNotNone(found)

    def test_02_pair_alias_exists(self):
        """Try to pair the test accessory"""
        self.controller.load_data(TestControllerPaired.controller_file.name)
        self.assertRaises(AlreadyPairedError, self.controller.perform_pairing, 'alias', '12:34:56:00:01:0B', '010-22-020')

    def test_02_paired_identify_wrong_method(self):
        """Try to identify an already paired accessory via the controller's method for unpaired accessories."""
        self.assertRaises(AlreadyPairedError, self.controller.identify, '12:34:56:00:01:0A')

    def test_03_get_accessories(self):
        self.controller.load_data(TestControllerPaired.controller_file.name)
        pairing = self.controller.get_pairings()['alias']
        result = pairing.list_accessories_and_characteristics()
        for characteristic in result[0]['services'][0]['characteristics']:
            if characteristic['format'] == 'bool':
                self.assertNotIn('maxDataLen', characteristic)
                self.assertNotIn('maxLen', characteristic)
        self.assertEqual(1, len(result))
        result = result[0]
        self.assertIn('aid', result)
        self.assertIn('services', result)

    def test_04_1_get_characteristic(self):
        self.controller.load_data(TestControllerPaired.controller_file.name)
        pairing = self.controller.get_pairings()['alias']
        result = pairing.get_characteristics([(1, 4)])
        self.assertIn((1, 4), result)
        self.assertIn('value', result[(1, 4)])
        self.assertEqual('lusiardi.de', result[(1, 4)]['value'])
        self.assertEqual(['value'], list(result[(1, 4)].keys()))

    def test_04_2_get_characteristics(self):
        self.controller.load_data(TestControllerPaired.controller_file.name)
        pairing = self.controller.get_pairings()['alias']
        result = pairing.get_characteristics([(1, 4), (1, 10)])
        self.assertIn((1, 4), result)
        self.assertIn('value', result[(1, 4)])
        self.assertEqual('lusiardi.de', result[(1, 4)]['value'])
        self.assertIn((1, 10), result)
        self.assertIn('value', result[(1, 10)])
        self.assertEqual(False, result[(1, 10)]['value'])

    def test_04_3_get_characteristic_with_events(self):
        """This tests the include_events flag on get_characteristics"""
        self.controller.load_data(TestControllerPaired.controller_file.name)
        pairing = self.controller.get_pairings()['alias']
        result = pairing.get_characteristics([(1, 4)], include_events=True)
        self.assertIn((1, 4), result)
        self.assertIn('value', result[(1, 4)])
        self.assertEqual('lusiardi.de', result[(1, 4)]['value'])
        self.assertIn('ev', result[(1, 4)])

    def test_04_4_get_characteristic_with_type(self):
        """This tests the include_type flag on get_characteristics"""
        self.controller.load_data(TestControllerPaired.controller_file.name)
        pairing = self.controller.get_pairings()['alias']
        result = pairing.get_characteristics([(1, 4)], include_type=True)
        self.assertIn((1, 4), result)
        self.assertIn('value', result[(1, 4)])
        self.assertEqual('lusiardi.de', result[(1, 4)]['value'])
        self.assertIn('type', result[(1, 4)])
        self.assertEqual('20', result[(1, 4)]['type'])

    def test_04_5_get_characteristic_with_perms(self):
        """This tests the include_perms flag on get_characteristics"""
        self.controller.load_data(TestControllerPaired.controller_file.name)
        pairing = self.controller.get_pairings()['alias']
        result = pairing.get_characteristics([(1, 4)], include_perms=True)
        self.assertIn((1, 4), result)
        self.assertIn('value', result[(1, 4)])
        self.assertEqual('lusiardi.de', result[(1, 4)]['value'])
        self.assertIn('perms', result[(1, 4)])
        self.assertEqual(['pr'], result[(1, 4)]['perms'])
        result = pairing.get_characteristics([(1, 3)], include_perms=True)
        self.assertEqual(['pw'], result[(1, 3)]['perms'])

    def test_04_4_get_characteristic_with_meta(self):
        """This tests the include_meta flag on get_characteristics"""
        self.controller.load_data(TestControllerPaired.controller_file.name)
        pairing = self.controller.get_pairings()['alias']
        result = pairing.get_characteristics([(1, 4)], include_meta=True)
        self.assertIn((1, 4), result)
        self.assertIn('value', result[(1, 4)])
        self.assertEqual('lusiardi.de', result[(1, 4)]['value'])
        self.assertIn('format', result[(1, 4)])
        self.assertEqual('string', result[(1, 4)]['format'])
        self.assertIn('maxLen', result[(1, 4)])
        self.assertEqual(64, result[(1, 4)]['maxLen'])

    def test_05_1_put_characteristic(self):
        """"""
        global value
        self.controller.load_data(TestControllerPaired.controller_file.name)
        pairing = self.controller.get_pairings()['alias']
        result = pairing.put_characteristics([(1, 10, 'On')])
        self.assertEqual(result, {})
        self.assertEqual(1, value)
        result = pairing.put_characteristics([(1, 10, 'Off')])
        self.assertEqual(result, {})
        self.assertEqual(0, value)

    def test_05_2_put_characteristic_do_conversion(self):
        """"""
        global value
        self.controller.load_data(TestControllerPaired.controller_file.name)
        pairing = self.controller.get_pairings()['alias']
        result = pairing.put_characteristics([(1, 10, 'On')], do_conversion=True)
        self.assertEqual(result, {})
        self.assertEqual(1, value)
        result = pairing.put_characteristics([(1, 10, 'Off')], do_conversion=True)
        self.assertEqual(result, {})
        self.assertEqual(0, value)

    def test_05_2_put_characteristic_do_conversion_wrong_value(self):
        """Tests that values that are not convertible to boolean cause a HomeKitTypeException"""
        self.controller.load_data(TestControllerPaired.controller_file.name)
        pairing = self.controller.get_pairings()['alias']
        self.assertRaises(FormatError, pairing.put_characteristics, [(1, 10, 'Hallo Welt')], do_conversion=True)

    def test_06_list_pairings(self):
        """Gets the listing of registered controllers of the device. Count must be 1."""
        self.controller.load_data(TestControllerPaired.controller_file.name)
        pairing = self.controller.get_pairings()['alias']
        result = pairing.list_pairings()
        self.assertEqual(1, len(result))
        result = result[0]
        self.assertIn('controllerType', result)
        self.assertEqual(result['controllerType'], 'admin')
        self.assertIn('publicKey', result)
        self.assertIn('permissions', result)
        self.assertEqual(result['permissions'], 1)
        self.assertIn('pairingId', result)

    def test_07_paired_identify(self):
        """Tests the paired variant of the identify method."""
        global identify
        self.controller.load_data(TestControllerPaired.controller_file.name)
        pairing = self.controller.get_pairings()['alias']
        result = pairing.identify()
        self.assertTrue(result)
        self.assertEqual(1, identify)
        identify = 0

    def test_99_remove_pairing(self):
        """Tests that a removed pairing is not present in the list of pairings anymore."""
        self.controller.load_data(TestControllerPaired.controller_file.name)
        self.controller.remove_pairing('alias')
        pairings = self.controller.get_pairings()
        self.assertNotIn('alias', pairings)
