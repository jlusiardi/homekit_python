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
    Data taken form table 5-8 Bonjour TXT Record Feature Flags on page 69.
    """

    def __init__(self):
        self._data = {
            0: 'Paired',
            1: 'Supports Pairing'
        }

    def __getitem__(self, item):
        if item in self._data:
            return self._data[item]

        raise KeyError('Item {item} not found'.format_map(item=item))


FeatureFlags = _FeatureFlags()
