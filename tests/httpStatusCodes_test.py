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

from homekit.http_impl import HttpStatusCodes


class TestHttpStatusCodes(unittest.TestCase):

    def test_1(self):
        self.assertEqual(HttpStatusCodes[HttpStatusCodes.INTERNAL_SERVER_ERROR], 'Internal Server Error')

    def test_unknown_code(self):
        self.assertRaises(KeyError, HttpStatusCodes.__getitem__, 99)