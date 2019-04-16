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


class CharacteristicFormats(object):
    """
    Values for characteristic's format taken from table 5-5 page 67
    """
    bool = 'bool'
    uint8 = 'uint8'
    uint16 = 'uint16'
    uint32 = 'uint32'
    uint64 = 'uint64'
    int = 'int'
    float = 'float'
    string = 'string'
    tlv8 = 'tlv8'
    data = 'data'


class _BleCharacteristicFormats(object):
    """
    Mapping taken from Table 6-36 page 129 and
    https://developer.nordicsemi.com/nRF5_SDK/nRF51_SDK_v4.x.x/doc/html/group___b_l_e___g_a_t_t___c_p_f___f_o_r_m_a_t_s.html
    """
    def __init__(self):
        self._formats = {
            0x01: 'bool',
            0x04: 'uint8',
            0x06: 'uint16',
            0x08: 'uint32',
            0x0A: 'uint64',
            0x10: 'int',
            0x14: 'float',
            0x19: 'string',
            0x1b: 'data'
        }

        self._formats_rev = {v: k for (k, v) in self._formats.items()}

    def get(self, key, default):
        return self._formats.get(key, default)

    def get_reverse(self, key, default):
        return self._formats_rev.get(key, default)


#
#   Have a singleton to avoid overhead
#
BleCharacteristicFormats = _BleCharacteristicFormats()
