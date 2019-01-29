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

import logging

from homekit.model import Categories
from homekit.model.status_flags import BleStatusFlags


def parse_manufacturer_specific(input_data):
    """
    Parse the manufacturer specific data as returned via Bluez ManufacturerData. This skips the data for LEN, ADT and
    CoID as specified in Chapter 6.4.2.2 of the spec on page 124. Data therefore starts at TY (must be 0x06).

    :param input_data: manufacturer specific data as bytes
    :return: a dict containing the type (key 'type', value 'HomeKit'), the status flag (key 'sf'), human readable
             version of the status flag (key 'flags'), the device id (key 'device_id'), the accessory category
             identifier (key 'acid'), human readable version of the category (key 'category'), the global state number
             (key 'gsn'), the configuration number (key 'cn') and the compatible version (key 'cv')
    """
    logging.debug('manufacturer specific data: %s', input_data.hex())

    # the type must be 0x06 as defined on page 124 table 6-29
    ty = input_data[0]
    input_data = input_data[1:]
    if ty == 0x06:
        ty = 'HomeKit'

        ail = input_data[0]
        logging.debug('advertising interval %s', '{0:02x}'.format(ail))
        length = ail & 0b00011111
        if length != 13:
            logging.debug('error with length of manufacturer data')
        input_data = input_data[1:]

        sf = input_data[0]
        flags = BleStatusFlags[sf]
        input_data = input_data[1:]

        device_id = (':'.join(input_data[:6].hex()[0 + i:2 + i] for i in range(0, 12, 2))).upper()
        input_data = input_data[6:]

        acid = int.from_bytes(input_data[:2], byteorder='little')
        input_data = input_data[2:]

        gsn = int.from_bytes(input_data[:2], byteorder='little')
        input_data = input_data[2:]

        cn = input_data[0]
        input_data = input_data[1:]

        cv = input_data[0]
        input_data = input_data[1:]
        if len(input_data) > 0:
            logging.debug('remaining data: %s', input_data.hex())
        return {'manufacturer': 'apple', 'type': ty, 'sf': sf, 'flags': flags, 'device_id': device_id, 'acid': acid,
                'gsn': gsn, 'cn': cn, 'cv': cv, 'category': Categories[int(acid)]}

    return {'manufacturer': 'apple', 'type': ty}
