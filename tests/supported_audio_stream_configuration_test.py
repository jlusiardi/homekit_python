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
import time

from homekit import Controller
from homekit import AccessoryServer
from homekit.model import Accessory
from homekit.model.services import LightBulbService
from homekit.model import mixin as model_mixin
from homekit.model import get_id
from tests.tools import AccessoryThread
from homekit.model.characteristics.rtp_stream.supported_audio_stream_configuration import \
    SupportedAudioStreamConfigurationCharacteristic, SupportedAudioStreamConfiguration, AudioCodecConfiguration, \
    AudioCodecParameters, SampleRate, BitRate, AudioCodecType, \
    ComfortNoiseSupport


class TestSupportedAudioStreamConfigurationCharacteristic(unittest.TestCase):
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
        value = SupportedAudioStreamConfiguration(
            AudioCodecConfiguration(
                AudioCodecType.OPUS,
                AudioCodecParameters(2, BitRate.VARIABLE, SampleRate.KHZ_16)
            ),
            ComfortNoiseSupport.NO_COMFORT_NOISE
        )
        cls.tlvChar = SupportedAudioStreamConfigurationCharacteristic(get_id(), value)
        lightBulbService.append_characteristic(cls.tlvChar)
        accessory.services.append(lightBulbService)
        cls.httpd.add_accessory(accessory)
        t = AccessoryThread(cls.httpd)
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
        for service in result[0]['services']:
            for characteristic in service['characteristics']:
                if characteristic['iid'] == self.__class__.tlvChar.iid:
                    self.assertIn('value', characteristic)
                    self.assertEqual('AQ4BAQMCCQEBAgIBAAMBAQIBAA==', characteristic['value'])
                    self.assertIn('format', characteristic)
                    self.assertEqual('tlv8', characteristic['format'])

    def test_get_characteristic(self):
        self.controller.load_data(self.controller_file.name)
        pairing = self.controller.get_pairings()['alias']

        self.__class__.tlvChar.value.comfort_noise_support = ComfortNoiseSupport.COMFORT_NOISE
        result = pairing.get_characteristics([(1, 11)])
        self.assertIn((1, 11), result)
        self.assertIn('value', result[(1, 11)])
        self.assertEqual('AQ4BAQMCCQEBAgIBAAMBAQIBAQ==', result[(1, 11)]['value'])
        self.assertEqual(['value'], list(result[(1, 11)].keys()))

        self.__class__.tlvChar.value.config.codec_type = AudioCodecType.OPUS
        result = pairing.get_characteristics([(1, 11)])
        self.assertIn((1, 11), result)
        self.assertIn('value', result[(1, 11)])
        self.assertEqual('AQ4BAQMCCQEBAgIBAAMBAQIBAQ==', result[(1, 11)]['value'])
        self.assertEqual(['value'], list(result[(1, 11)].keys()))

    def test_get_characteristic_with_getter(self):
        self.controller.load_data(self.controller_file.name)
        pairing = self.controller.get_pairings()['alias']

        def get():
            return SupportedAudioStreamConfiguration(
                AudioCodecConfiguration(
                    AudioCodecType.AAC_ELD,
                    AudioCodecParameters(1, BitRate.CONSTANT, SampleRate.KHZ_8)
                ),
                ComfortNoiseSupport.COMFORT_NOISE
            )

        self.__class__.tlvChar.set_get_value_callback(get)
        result = pairing.get_characteristics([(1, 11)])
        self.__class__.tlvChar.set_get_value_callback(None)
        self.assertIn((1, 11), result)
        self.assertIn('value', result[(1, 11)])
        self.assertEqual('AQ4BAQICCQEBAQIBAQMBAAIBAQ==', result[(1, 11)]['value'])
        self.assertEqual(['value'], list(result[(1, 11)].keys()))

    def test_StreamingStatus_from_bytes(self):
        data = SupportedAudioStreamConfiguration.from_bytes(
            b'\x01\x0e\x01\x01\x02\x02\t\x01\x01\x01\x02\x01\x01\x03\x01\x00\x02\x01\x01')
        expected = SupportedAudioStreamConfiguration(
            AudioCodecConfiguration(
                AudioCodecType.AAC_ELD,
                AudioCodecParameters(1, BitRate.CONSTANT, SampleRate.KHZ_8)
            ),
            ComfortNoiseSupport.COMFORT_NOISE
        )
        self.assertEqual(expected, data)
