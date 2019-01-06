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

import logging
from argparse import ArgumentParser

from homekit.controller.ble_impl.discovery import DiscoveryDeviceManager


def discover(adapter, timeout=10):
    manager = DiscoveryDeviceManager(adapter)
    manager.start_discovery()
    manager.set_timeout(timeout * 1000)
    manager.run()

    return manager._devices.values()


if __name__ == '__main__':
    arg_parser = ArgumentParser(description='HomeKit BLE discover app - '\
                                            'list all HomeKit Bluetooth LE devices in range. *MUST* be running as '\
                                            'root because we need to use hciconfig, hcitool and hci dump in order to '\
                                            'activate the adapter, start scanning and dump the responses. Sorry about '\
                                            'that.')
    arg_parser.add_argument('-t', action='store', required=False, dest='timeout', type=int, default=10,
                            help='Number of seconds to wait')
    arg_parser.add_argument('--adapter', action='store', dest='adapter', default='hci0',
                            help='the bluetooth adapter to be used (defaults to hci0)')
    arg_parser.add_argument('--log', action='store', dest='loglevel', help='set to DEBUG to see the logs')
    args = arg_parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(filename)s:%(lineno)04d %(levelname)s %(message)s')
    if args.loglevel:
        getattr(logging, args.loglevel.upper())
        numeric_level = getattr(logging, args.loglevel.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % args.loglevel)
        logging.getLogger().setLevel(numeric_level)

    logging.debug('using adapter %s', args.adapter)

    devices = discover(args.adapter, args.timeout)

    print()
    for device in devices:
        data = device.homekit_discovery_data
        print('Name: {name}'.format(name=device.name))
        print('MAC: {mac}'.format(mac=device.mac_address))
        print('Configuration number (c#): {conf}'.format(conf=data['cn']))
        print('Device ID (id): {id}'.format(id=data['deviceId']))
        print('Compatible Version (cv): {cv}'.format(cv=data['cv']))
        print('State Number (s#): {sn}'.format(sn=data['gsn']))
        print('Status Flags (sf): {sf}'.format(sf=data['sf']))
        print('Category Identifier (ci): {c} (Id: {ci})'.format(c=data['category'],
                                                                ci=data['acid']))
        print()
