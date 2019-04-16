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


class _IpStatusFlags(object):
    """
    Data taken form table 5-9 page 70
    """

    def __getitem__(self, item):
        i = int(item)
        result = []
        if i & 0x01:
            result.append('Accessory has not been paired with any controllers.')
            i = i - 0x01
        else:
            result.append('Accessory has been paired.')
        if i & 0x02:
            result.append('Accessory has not been configured to join a Wi-Fi network.')
            i = i - 0x02
        if i & 0x04:
            result.append('A problem has been detected on the accessory.')
            i = i - 0x04
        if i == 0:
            return ' '.join(result)
        else:
            raise KeyError('Item {item} not found'.format(item=item))


class _BleStatusFlags(object):
    """
    Data taken form table 6-32 page 125
    """

    def __getitem__(self, item):
        i = int(item)
        result = []
        if i & 0x01:
            result.append('The accessory has not been paired with any controllers.')
            i = i - 0x01
        else:
            result.append('The accessory has been paired with a controllers.')
        if i == 0:
            return ' '.join(result)
        else:
            raise KeyError('Item {item} not found'.format(item=item))


IpStatusFlags = _IpStatusFlags()
BleStatusFlags = _BleStatusFlags()
