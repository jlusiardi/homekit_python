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

from homekit.model.services import ServicesTypes


class TestServiceTypes(unittest.TestCase):

    def test_getitem_forward(self):
        self.assertEqual(ServicesTypes['3E'], 'public.hap.service.accessory-information')

    def test_getitem_reverse(self):
        self.assertEqual(ServicesTypes['public.hap.service.accessory-information'], '3E')

    def test_getitem_notfound(self):
        self.assertEqual(ServicesTypes['1337'], 'Unknown Service: 1337')

    def test_get_short(self):
        self.assertEqual(ServicesTypes.get_short('00000086-0000-1000-8000-0026BB765291'), 'occupancy')

    def test_get_short_lowercase(self):
        self.assertEqual(ServicesTypes.get_short('00000086-0000-1000-8000-0026bb765291'), 'occupancy')

    def test_get_short_no_baseid(self):
        self.assertEqual(ServicesTypes.get_short('00000023-0000-1000-8000-NOTBASEID'),
                         'Unknown Service: 00000023-0000-1000-8000-NOTBASEID')

    def test_get_short_no_service(self):
        self.assertEqual(ServicesTypes.get_short('00000023-0000-1000-8000-0026BB765291'),
                         'Unknown Service: 00000023-0000-1000-8000-0026BB765291')

    def test_get_uuid(self):
        self.assertEqual(ServicesTypes.get_uuid('public.hap.service.doorbell'), '00000121-0000-1000-8000-0026BB765291')

    def test_get_uuid_no_service(self):
        self.assertRaises(Exception, ServicesTypes.get_uuid, 'public.hap.service.NO_A_SERVICE')
