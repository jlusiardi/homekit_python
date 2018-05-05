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
import sys

from homekit.http_client import HomeKitHTTPConnection
from homekit.zeroconf_ import find_device_ip_and_port
from homekit.protocol import get_session_keys


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


def create_session(file):
    """
    try to obtain IP and port from the given file and establish a session to a HomeKit accessory. This function covers
    IP/ports that might have changed since last run and updates the file accordingly.

    :param file: the path to the file where the data is stored
    :return:
        conn: an instance of HomeKitHTTPConnection
        c2a_key: the key used for communication from controller to accessory
        a2c_key: the key used for communication from accessory to controller
    """
    conn = None
    c2a_key = None
    a2c_key = None

    # load file with pairing data
    pairing_data = load_pairing(file)
    if pairing_data is None:
        print('File {file} not found!'.format(file=file))
        sys.exit(-1)

    # we need ip and port of the device
    connected = False
    if 'AccessoryIP' in pairing_data and 'AccessoryPort' in pairing_data:
        # if it is known, try it
        accessory_ip = pairing_data['AccessoryIP']
        accessory_port = pairing_data['AccessoryPort']
        conn = HomeKitHTTPConnection(accessory_ip, port=accessory_port)
        try:
            conn.connect()
            c2a_key, a2c_key = get_session_keys(conn, pairing_data)
            connected = True
        except Exception as e:
            connected = False

    if not connected:
        # no connection yet, so ip / port might have changed and we need to fall back to slow zeroconf lookup
        device_id = pairing_data['AccessoryPairingID']
        connection_data = find_device_ip_and_port(device_id)
        if connection_data is None:
            print('Device {id} not found'.format(id=device_id))
            sys.exit(-1)
        conn = HomeKitHTTPConnection(connection_data['ip'], port=connection_data['port'])
        pairing_data['AccessoryIP'] = connection_data['ip']
        pairing_data['AccessoryPort'] = connection_data['port']
        save_pairing(file, pairing_data)
        c2a_key, a2c_key = get_session_keys(conn, pairing_data)

    return conn, c2a_key, a2c_key
