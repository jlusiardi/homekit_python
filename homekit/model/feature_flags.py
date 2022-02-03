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

class _FeatureFlags(object):
    """
    Data taken from table 5-8 Bonjour TXT Record Feature Flags on page 69.
    """

    APPLE_MFI_COPROCESSOR = 0x01
    SOFTWARE_MFI_AUTH = 0x02

    def __init__(self):
        self._data = {
            0x00: 'No support for HAP Pairing', # this might also be uncertified
            self.APPLE_MFI_COPROCESSOR: 'Apple authentication coprocessor',
            self.SOFTWARE_MFI_AUTH: 'Software authentication',
        }

    def __getitem__(self, item: int) -> str:
        data = []
        if 0 != (item & self.APPLE_MFI_COPROCESSOR):
            data.append(self._data[self.APPLE_MFI_COPROCESSOR])
        if 0 != (item & self.SOFTWARE_MFI_AUTH):
            data.append(self._data[self.SOFTWARE_MFI_AUTH])

        if data:
            return 'Supports HAP Pairing with ' + ' and '.join(data)
        elif 0 == item:
            # Note: this may change if feature flags will have more flags!
            return self._data[0]

        raise KeyError('Item {item} not found'.format(item=item))


FeatureFlags = _FeatureFlags()
