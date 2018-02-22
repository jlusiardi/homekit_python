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

import json


def load_pairing(file: str) -> dict:
    """
    loads data for an existing pairing from the file.

    :param file: the file name
    :return: a dict containing the pairing data or None if file was not found
    """
    try:
        with open(file, 'r') as input_fp:
            return json.load(input_fp)
    except FileNotFoundError:
        return None


def save_pairing(file: str, pairing_data: dict):
    """
    save the data for an existing pairing.

    :param file: the file name
    :param pairing_data: a dict containing the pairing data
    :return: None
    """
    with open(file, 'w') as output_fp:
        json.dump(pairing_data, output_fp, indent=4)
