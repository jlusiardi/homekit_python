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

import threading
import time
import logging
from argparse import ArgumentParser
import sys
import os
from homekit.model import Categories

from staging import gatt


class Killer(threading.Thread):

    def __init__(self, manager, timeout):
        threading.Thread.__init__(self)
        self.timeout = timeout
        self.manager = manager

    def run(self):
        time.sleep(self.timeout)
        self.manager.stop()


def parse_manufacturer_specific(input_data):
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
        if sf == 0:
            sf = 'paired'
        elif sf == 1:
            sf = 'unpaired'
        else:
            sf = 'error'
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
        return {'manufacturer': 'apple', 'type': ty, 'sf': sf, 'deviceId': device_id, 'acid': acid,
                'gsn': gsn, 'cn': cn, 'cv': cv, 'category': Categories[int(acid)]}

    return {'manufacturer': 'apple', 'type': ty}


class Device(gatt.Device):

    homekit_discovery_data = None

    def __init__(self, *args, **kwargs):
        gatt.Device.__init__(self, *args, **kwargs, managed=False)

        self.name = self._properties.Get('org.bluez.Device1', 'Alias')

        mfr_data = self._properties.Get('org.bluez.Device1', 'ManufacturerData')
        mfr_data = dict((int(k), bytes(bytearray(v))) for (k, v) in mfr_data.items())

        if 76 not in mfr_data:
            return

        parsed = parse_manufacturer_specific(mfr_data[76])

        if parsed['type'] != 'HomeKit':
            return

        self.homekit_discovery_data = parsed

 

class DeviceManager(gatt.DeviceManager):

    discover_callback = None

    def make_device(self, mac_address):
        device = Device(mac_address=mac_address, manager=self)
        if not device.homekit_discovery_data:
            return
        self._manage_device(device)
        if self.discover_callback:
            self.discover_callback(device)

    def start_discovery(self, callback=None):
        self.discover_callback = callback
        return gatt.DeviceManager.start_discovery(self)


def discover(adapter, timeout=10):
    manager = DeviceManager(adapter)
    manager.start_discovery()
    Killer(manager, timeout).start()
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
