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
import sys
import logging

from homekit.log_support import setup_logging, add_log_arguments
from homekit.controller import Controller


def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit BLE discover app - '
                                                 'list all HomeKit Bluetooth LE devices in range')
    parser.add_argument('-t', action='store', required=False, dest='timeout', type=int, default=10,
                        help='Number of seconds to wait (defaults to 10)')
    parser.add_argument('--adapter', action='store', dest='adapter', default='hci0',
                        help='the bluetooth adapter to be used (defaults to hci0)')
    parser.add_argument('-u', action='store_true', required=False, dest='unpaired_only',
                        help='If activated, this option will show only unpaired HomeKit BLE Devices')
    add_log_arguments(parser)
    return parser.parse_args()


if __name__ == '__main__':
    args = setup_args_parser()
    setup_logging(args.loglevel)

    try:
        devices = Controller.discover_ble(args.timeout, args.adapter)
    except Exception as e:
        print(e)
        logging.debug(e, exc_info=True)
        sys.exit(-1)

    print()
    for device in devices:
        if args.unpaired_only and device['sf'] == 0:
            continue
        print('Name: {name}'.format(name=device['name']))
        print('MAC: {mac}'.format(mac=device['mac']))
        print('Configuration number (cn): {conf}'.format(conf=device['cn']))
        print('Device ID (id): {id}'.format(id=device['device_id']))
        print('Compatible Version (cv): {cv}'.format(cv=device['cv']))
        print('Global State Number (s#): {sn}'.format(sn=device['gsn']))
        print('Status Flags (sf): {sf} (Flag: {flags})'.format(sf=device['flags'], flags=device['sf']))
        print('Category Identifier (ci): {c} (Id: {ci})'.format(c=device['category'], ci=device['acid']))
        print()
    sys.exit(0)
