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

from homekit.zeroconf_ import get_from_properties


class TestZeroconf(unittest.TestCase):

    def test_existing_key(self):
        props = {b'c#': b'259'}
        val = get_from_properties(props, b'c#')
        self.assertEqual('259', val)

    def test_non_existing_key_no_default(self):
        props = {b'c#': b'259'}
        val = get_from_properties(props, b's#')
        self.assertEqual(None, val)

    def test_non_existing_key_case_insensitive(self):
        props = {b'C#': b'259', b'heLLo': b'World'}
        val = get_from_properties(props, b'c#')
        self.assertEqual(None, val)
        val = get_from_properties(props, b'c#', case_sensitive=True)
        self.assertEqual(None, val)
        val = get_from_properties(props, b'c#', case_sensitive=False)
        self.assertEqual('259', val)

        val = get_from_properties(props, b'HEllo', case_sensitive=False)
        self.assertEqual('World', val)

    def test_non_existing_key_with_default(self):
        props = {b'c#': b'259'}
        val = get_from_properties(props, b's#', default='1')
        self.assertEqual('1', val)

    def test_non_existing_key_with_default_non_string(self):
        props = {b'c#': b'259'}
        val = get_from_properties(props, b's#', default=1)
        self.assertEqual('1', val)
