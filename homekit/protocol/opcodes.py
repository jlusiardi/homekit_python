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


class _HapBleOpCodes(object):
    """
    This data is taken from Table 6-7 HAP Opcode Description on page 97.
    """
    CHAR_SIG_READ = 0x01
    CHAR_WRITE = 0x02
    CHAR_READ = 0x03
    CHAR_TIMED_WRITE = 0x04
    CHAR_EXEC_WRITE = 0x05
    SERV_SIG_READ = 0x06

    def __init__(self):
        self._codes = {
            _HapBleOpCodes.CHAR_SIG_READ: 'HAP-Characteristic-Signature-Read',
            _HapBleOpCodes.CHAR_WRITE: 'HAP-Characteristic-Write',
            _HapBleOpCodes.CHAR_READ: 'HAP-Characteristic-Read',
            _HapBleOpCodes.CHAR_TIMED_WRITE: 'HAP-Characteristic-Timed-Write',
            _HapBleOpCodes.CHAR_EXEC_WRITE: 'HAP-Characteristic-Execute-Write',
            _HapBleOpCodes.SERV_SIG_READ: 'HAP-Service-Signature-Read',
        }

        self._categories_rev = {self._codes[k]: k for k in self._codes.keys()}

    def __getitem__(self, item):
        if item in self._codes:
            return self._codes[item]

        raise KeyError('Item {item} not found'.format(item=item))


HapBleOpCodes = _HapBleOpCodes()
