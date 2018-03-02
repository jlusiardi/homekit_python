#!/usr/bin/env python3

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
import argparse
import http.client
import sys

from homekit import find_device_ip_and_port, SecureHttp, load_pairing, get_session_keys, HapStatusCodes


def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit perform app - performs operations on paired devices')
    parser.add_argument('-f', action='store', required=True, dest='file', help='File with the pairing data')
    parser.add_argument('-c', action='store', required=False, dest='characteristics')
    parser.add_argument('-v', action='store', required=False, dest='value')

    return parser


if __name__ == '__main__':
    parser = setup_args_parser()
    args = parser.parse_args()

    pairing_data = load_pairing(args.file)
    if pairing_data is None:
        print('File {file} not found!'.format(file=args.file))
        sys.exit(-1)

    deviceId = pairing_data['AccessoryPairingID']

    connection_data = find_device_ip_and_port(deviceId)
    if connection_data is None:
        print('Device {id} not found'.format(id=deviceId))
        sys.exit(-1)

    conn = http.client.HTTPConnection(connection_data['ip'], port=connection_data['port'])

    controllerToAccessoryKey, accessoryToControllerKey = get_session_keys(conn, pairing_data)

    if not args.characteristics:
        parser.print_help()
        sys.exit(-1)
    if not args.value:
        parser.print_help()
        sys.exit(-1)

    tmp = args.characteristics.split('.')
    aid = int(tmp[0])
    iid = int(tmp[1])
    value = args.value

    sec_http = SecureHttp(conn.sock, accessoryToControllerKey, controllerToAccessoryKey)

    body = json.dumps({'characteristics': [{'aid': aid, 'iid': iid, 'value': value}]})
    print(body)
    response = sec_http.put('/characteristics', body)
    data = response.read().decode()
    if response.code != 204:
        data = json.loads(data)
        code = data['status']
        print('put_characteristics failed because: {reason} ({code})'.format(reason=HapStatusCodes[code], code=code))
    else:
        print('put_characteristics succeeded')

    conn.close()
