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
import subprocess
import time
import logging
from argparse import ArgumentParser
import sys
import os
import struct
from homekit.model import Categories
from staging.version import VERSION

# These constants are all taken from https://www.bluetooth.com/specifications/bluetooth-core-specification and are
# defined on the pages mentioned.
HCI_EVENT = 0x04  # page 2400

LE_META = 0x3e  # page 1190

LE_ADVERTISING_REPORT = 0x02  # page 1193

EVENT_TYPE_CONNECTABLE_UNDIRECTED_ADVERTISING = 0x00  # page 1193
EVENT_TYPE_NONCONNECTABLE_UNDIRECTED_ADVERTISING = 0x03  # page 1193
EVENT_TYPE_SCAN_RESPONSE = 0x04   # page 1194

devices = {}


class Killer(threading.Thread):
    def __init__(self, timeout, process):
        threading.Thread.__init__(self)
        self.timeout = timeout
        self.process = process

    def run(self):
        time.sleep(self.timeout)
        self.process.kill()


def parse_manufacturer_specific(input_data):
    logging.debug('manufacturer specific data: %s', input_data.hex())

    # parse the manufacturer, this must be 0x4C 0x00 as defined on page 124 table 6-29
    coid = input_data[:2]
    input_data = input_data[2:]
    if coid == b'\x4c\x00':
        coid = 'apple'

    # the type must be 0x06 as defined on page 124 table 6-29
    ty = input_data[0]
    input_data = input_data[1:]
    if coid == 'apple' and ty == 0x06:
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
        return {'manufacturer': coid, 'type': ty, 'sf': sf, 'deviceId': device_id, 'acid': acid,
                'gsn': gsn, 'cn': cn, 'cv': cv, 'category': Categories[int(acid)]}

    return {'manufacturer': coid, 'type': ty}


def parse_ble_meta_data(input_data):
    total_length = input_data[0]
    input_data = input_data[1:1 + total_length]
    logging.debug('length %d data %s',total_length, input_data.hex())

    if total_length != len(input_data):
        logging.error('length issue %d %d -- %s', total_length, len(input_data), input_data.hex())
        return

    if not input_data[0] == LE_ADVERTISING_REPORT:
        logging.error('No Sub Event: LE Advertising Report %s', input_data.hex())
        return
    input_data = input_data[1:]

    if input_data[0] != 0x01:
        # TODO: how does an advertising look if there are more than one reports?
        logging.error('No Num Reports: %d', input_data[0], input_data.hex())
        return
    input_data = input_data[1:]

    # Bluetooth Core Spec 5.0 page 1193
    if input_data[0] == EVENT_TYPE_CONNECTABLE_UNDIRECTED_ADVERTISING:
        event_type = 'Connectable Undirected Advertising'
    elif input_data[0] == EVENT_TYPE_NONCONNECTABLE_UNDIRECTED_ADVERTISING:
        event_type = 'Non-Connectable Undirected Advertising'
    elif input_data[0] == EVENT_TYPE_SCAN_RESPONSE:
        event_type = 'Scan Response'
    else:
        logging.error('Unknown Event Type:', input_data[0], ' -- ', input_data.hex())
        event_type = 'unknown'
    input_data = input_data[1:]

    # Bluetooth Core Spec 5.0 page 1194
    if input_data[0] == 0x00:
        # Peer Address Type: Public Device Address (0x00)
        address_type = 'public'
    elif input_data[0] == 0x01:
        address_type = 'random'
    else:
        print('Unknown Address Type:', input_data[0], ' -- ', input_data.hex())
        address_type = 'unknown'
        # return
    input_data = input_data[1:]

    # Bluetooth Core Spec 5.0 page 1194
    mac = input_data[:6].hex().upper()
    mac = mac[10:12] + ':' + mac[8:10] + ':' + mac[6:8] + ':' + mac[4:6] + ':' + mac[2:4] + ':' + mac[0:2]
    if mac not in devices:
        devices[mac] = {}

    devices[mac]['address_type'] = address_type
    devices[mac]['event_type'] = event_type
    input_data = input_data[6:]

    # Bluetooth Core Spec 5.0 page 1194
    data_length = input_data[0]

    # Bluetooth Core Spec 5.0 page 1194
    remaining_data = input_data[1 + data_length:]
    rssi = struct.unpack('b',remaining_data)[0]
    devices[mac]['rssi'] = rssi
    logging.debug('rssi: %d', rssi)

    input_data = input_data[1:1 + data_length]

    while len(input_data) > 0:
        # the format of the advertising data is defined in Bluetooth Core Spec 5.0 page 2086
        part_length = input_data[0]
        input_data = input_data[1:]

        part_type = input_data[0]
        input_data = input_data[1:]

        part_data = input_data[0:part_length - 1]
        input_data = input_data[part_length - 1:]

        # the part types are defined in https://www.bluetooth.com/specifications/assigned-numbers/generic-access-profile
        if part_type == 1:
            devices[mac]['Flags'] = part_data
        elif part_type == 8:
            devices[mac]['Short Device Name'] = part_data
        elif part_type == 9:
            devices[mac]['Device Name'] = part_data.decode('ascii')
        elif part_type == 255:
            devices[mac]['Manufacturer Specific'] = parse_manufacturer_specific(part_data)
        else:
            devices[mac][part_type] = part_data


def which(program):
    """
    function to check if an executable is somewhere in the PATH and return it with full path.

    taken from https://stackoverflow.com/a/377028
    """

    def is_exe(file):
        return os.path.isfile(file) and os.access(file, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


if __name__ == '__main__':
    arg_parser = ArgumentParser(description="GATT Connect Demo")
    arg_parser.add_argument('-t', action='store', required=False, dest='timeout', type=int, default=10,
                            help='Number of seconds to wait')
    arg_parser.add_argument('--adapter', action='store', dest='adapter', default='hci0')
    arg_parser.add_argument('--log', action='store', dest='loglevel')
    args = arg_parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(filename)s:%(lineno)04d %(levelname)s %(message)s')
    if args.loglevel:
        getattr(logging, args.loglevel.upper())
        numeric_level = getattr(logging, args.loglevel.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % args.loglevel)
        logging.getLogger().setLevel(numeric_level)

    logging.debug('running version: %s', VERSION)
    logging.debug('using adapter %s', args.adapter)

    hciconfig = which('hciconfig')
    hcitool = which('hcitool')
    hcidump = which('hcidump')
    if not hciconfig:
        print('hciconfig could not be found in the PATH!')
        sys.exit(-1)
    if not hcitool:
        print('hcitool could not be found in the PATH!')
        sys.exit(-1)
    if not hcidump:
        print('hcidump could not be found in the PATH!')
        sys.exit(-1)

    command = [hciconfig, args.adapter, 'up']
    logging.debug('Executing \'%s\'', ' '.join(command))
    p0 = subprocess.Popen(command, stdout=subprocess.PIPE)

    command = [hcitool, '-i', args.adapter, 'lescan', '--duplicates']
    logging.debug('Executing \'%s\'', ' '.join(command))
    p0 = subprocess.Popen(command, stdout=subprocess.PIPE)
    Killer(args.timeout, p0).start()

    command = [hcidump, '-i', args.adapter, '--raw', '2>&1']
    logging.debug('Executing \'%s\'', ' '.join(command))
    p1 = subprocess.Popen(command, stdout=subprocess.PIPE)
    Killer(args.timeout, p1).start()

    data = None
    # we have to parse the output of hcidump here: it looks like
    # > 04 3E 2B 02 01 00 01 64 9F ED 22 D1 EB 1F 02 01 06 16 FF 4C
    #   00 06 31 01 84 BF 32 C2 8F 04 0A 00 02 00 01 02 9E 5D 64 42
    #   04 08 4B 6F 6F D7
    # > ...
    for line in p1.stdout:
        # lines from hci dump starting with > (ASCII 62) mark a new package
        if line[0] == 62:
            # a new packet is started, so we handle the old packet's data now
            if data:
                data = data.decode('ascii')
                data = bytes.fromhex(data.replace(' ', ''))
                logging.debug('data %s', data.hex())
                if data[0] == HCI_EVENT and data[1] == LE_META:
                    parse_ble_meta_data(data[2:])
            # data of the new packet, but without the starting '> ' and the ending line break
            data = line[2:-2]
        elif data is not None:
            # we already have read at least a packet start and now add the following lines (ignoring space and line
            # break in the beginning and end.
            data = (data + line[1:-2])
            raw = data

    print()
    for mac in devices:
        device = devices[mac]
        if 'Manufacturer Specific' in device \
                and 'type' in device['Manufacturer Specific'] \
                and device['Manufacturer Specific']['type'] == 'HomeKit':
            print('Name: {name}'.format(name=device['Device Name']))
            print('MAC: {mac}'.format(mac=mac))
            print('Configuration number (c#): {conf}'.format(conf=device['Manufacturer Specific']['cn']))
            print('Device ID (id): {id}'.format(id=device['Manufacturer Specific']['deviceId']))
            print('Compatible Version (cv): {cv}'.format(cv=device['Manufacturer Specific']['cv']))
            print('State Number (s#): {sn}'.format(sn=device['Manufacturer Specific']['gsn']))
            print('Status Flags (sf): {sf}'.format(sf=device['Manufacturer Specific']['sf']))
            print('Category Identifier (ci): {c} (Id: {ci})'.format(c=device['Manufacturer Specific']['category'],
                                                                    ci=device['Manufacturer Specific']['acid']))
            print()
