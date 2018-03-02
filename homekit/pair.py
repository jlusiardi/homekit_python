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

import argparse
import http.client
import uuid
import sys

from homekit import find_device_ip_and_port, save_pairing, perform_pair_setup


def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit pairing app')
    parser.add_argument('-d', action='store', required=True, dest='device')
    parser.add_argument('-p', action='store', required=True, dest='pin')
    parser.add_argument('-f', action='store', required=True, dest='file')
    return parser.parse_args()


iOSPairingId = str(uuid.uuid4())

if __name__ == '__main__':
    args = setup_args_parser()

    connection_data = find_device_ip_and_port(args.device)
    if connection_data is None:
        print('Device {id} not found'.format(id=args.device))
        sys.exit(-1)

    conn = http.client.HTTPConnection(connection_data['ip'], port=connection_data['port'])

    pairing = perform_pair_setup(conn, args.pin, iOSPairingId)

    save_pairing(args.file, pairing)
