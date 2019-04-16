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
from zeroconf import Zeroconf, ServiceInfo
import socket

from homekit.zeroconf_impl import find_device_ip_and_port, discover_homekit_devices, get_from_properties


class TestZeroconf(unittest.TestCase):

    @staticmethod
    def find_device(desc, result):
        test_device = None
        for device in result:
            device_found = True
            for key in desc:
                expected_val = desc[key]
                if device[key] != expected_val:
                    device_found = False
                    break
            if device_found:
                test_device = device
                break
        return test_device

    def test_find_without_device(self):
        result = find_device_ip_and_port('00:00:00:00:00:00', 1)
        self.assertIsNone(result)

    def test_find_with_device(self):
        zeroconf = Zeroconf()
        desc = {'id': '00:00:02:00:00:02'}
        info = ServiceInfo('_hap._tcp.local.', 'foo1._hap._tcp.local.', address=socket.inet_aton('127.0.0.1'),
                           port=1234, properties=desc, weight=0, priority=0)
        zeroconf.unregister_all_services()
        zeroconf.register_service(info, allow_name_change=True)

        result = find_device_ip_and_port('00:00:02:00:00:02', 10)

        zeroconf.unregister_all_services()

        self.assertIsNotNone(result)
        self.assertEqual(result['ip'], '127.0.0.1')

    def test_discover_homekit_devices(self):
        zeroconf = Zeroconf()
        desc = {'c#': '1', 'id': '00:00:01:00:00:02', 'md': 'unittest', 's#': '1', 'ci': '5', 'sf': '0'}
        info = ServiceInfo('_hap._tcp.local.', 'foo2._hap._tcp.local.', address=socket.inet_aton('127.0.0.1'),
                           port=1234, properties=desc, weight=0, priority=0)
        zeroconf.unregister_all_services()
        zeroconf.register_service(info, allow_name_change=True)

        result = discover_homekit_devices()
        test_device = self.find_device(desc, result)

        zeroconf.unregister_all_services()

        self.assertIsNotNone(test_device)

    def test_discover_homekit_devices_missing_c(self):
        zeroconf = Zeroconf()
        desc = {'id': '00:00:01:00:00:03', 'md': 'unittest', 's#': '1', 'ci': '5', 'sf': '0'}
        info = ServiceInfo('_hap._tcp.local.', 'foo3._hap._tcp.local.', address=socket.inet_aton('127.0.0.1'),
                           port=1234, properties=desc, weight=0, priority=0)
        zeroconf.unregister_all_services()
        zeroconf.register_service(info, allow_name_change=True)

        result = discover_homekit_devices()
        test_device = self.find_device(desc, result)

        zeroconf.unregister_all_services()

        self.assertIsNone(test_device)

    def test_discover_homekit_devices_missing_md(self):
        zeroconf = Zeroconf()
        desc = {'c#': '1', 'id': '00:00:01:00:00:04', 's#': '1', 'ci': '5', 'sf': '0'}
        info = ServiceInfo('_hap._tcp.local.', 'foo4._hap._tcp.local.', address=socket.inet_aton('127.0.0.1'),
                           port=1234, properties=desc, weight=0, priority=0)
        zeroconf.unregister_all_services()
        zeroconf.register_service(info, allow_name_change=True)

        result = discover_homekit_devices()
        test_device = self.find_device(desc, result)

        zeroconf.unregister_all_services()

        self.assertIsNone(test_device)

    def test_existing_key(self):
        props = {'c#': '259'}
        val = get_from_properties(props, 'c#')
        self.assertEqual('259', val)

    def test_non_existing_key_no_default(self):
        props = {'c#': '259'}
        val = get_from_properties(props, 's#')
        self.assertEqual(None, val)

    def test_non_existing_key_case_insensitive(self):
        props = {'C#': '259', 'heLLo': 'World'}
        val = get_from_properties(props, 'c#')
        self.assertEqual(None, val)
        val = get_from_properties(props, 'c#', case_sensitive=True)
        self.assertEqual(None, val)
        val = get_from_properties(props, 'c#', case_sensitive=False)
        self.assertEqual('259', val)

        val = get_from_properties(props, 'HEllo', case_sensitive=False)
        self.assertEqual('World', val)

    def test_non_existing_key_with_default(self):
        props = {'c#': '259'}
        val = get_from_properties(props, 's#', default='1')
        self.assertEqual('1', val)

    def test_non_existing_key_with_default_non_string(self):
        props = {'c#': '259'}
        val = get_from_properties(props, 's#', default=1)
        self.assertEqual('1', val)
