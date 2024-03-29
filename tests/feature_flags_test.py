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

from homekit.model.feature_flags import FeatureFlags


class TestFeatureFlags(unittest.TestCase):

    def test_no_support_hap_pairing(self):
        self.assertEqual(FeatureFlags[0x00], 'No support for HAP Pairing')

    def test_support_hap_pairing_hw(self):
        self.assertEqual(0x01, FeatureFlags.APPLE_MFI_COPROCESSOR)
        self.assertEqual(FeatureFlags[0x01], 'Supports HAP Pairing with Apple authentication coprocessor')

    def test_support_hap_pairing_sw(self):
        self.assertEqual(0x02, FeatureFlags.SOFTWARE_MFI_AUTH)
        self.assertEqual(FeatureFlags[0x02], 'Supports HAP Pairing with Software authentication')

    def test_support_hap_pairing_hw_sw(self):
        self.assertEqual(FeatureFlags[FeatureFlags.APPLE_MFI_COPROCESSOR | FeatureFlags.SOFTWARE_MFI_AUTH],
                         'Supports HAP Pairing with Apple authentication coprocessor and Software authentication')

    def test_support_hap_pairing_unknown(self):
        with self.assertRaises(KeyError):
            FeatureFlags[0x80]
