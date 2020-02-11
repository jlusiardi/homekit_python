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
import tlv8
import base64

from homekit.exceptions import FormatError
from homekit.model.characteristics import CharacteristicFormats
from homekit.controller.tools import check_convert_value


class CheckConvertLevelTest(unittest.TestCase):

    def test_tlv(self):
        tgt_type = CharacteristicFormats.tlv8
        tlv8_val = tlv8.encode([tlv8.Entry(1, 3)])[:-1]
        val = base64.b64encode(tlv8_val).decode()
        self.assertRaises(FormatError, check_convert_value, val, tgt_type)
