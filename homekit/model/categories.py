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


class _Categories(object):
    """
    This data is taken from Table 12-3 Accessory Categories on page 254. Values above 19 are reserved.
    """

    def __init__(self):
        self._categories = {
            1: 'Other',
            2: 'Bridge',
            3: 'Fan',
            4: 'Garage',
            5: 'Lightbulb',
            6: 'Door Lock',
            7: 'Outlet',
            8: 'Switch',
            9: 'Thermostat',
            10: 'Sensor',
            11: 'Security System',
            12: 'Door',
            13: 'Window',
            14: 'Window Covering',
            15: 'Programmable Switch',
            16: 'Range Extender',
            17: 'IP Camera',
            18: 'Video Door Bell',
            19: 'Air Purifier'
        }

        self._categories_rev = {self._categories[k]: k for k in self._categories.keys()}

    def __getitem__(self, item):
        if item in self._categories:
            return self._categories[item]

        if item in self._categories_rev:
            return self._categories_rev[item]

        raise KeyError('Item {item} not found'.format_map(item=item))


Categories = _Categories()
