#!/usr/bin/env python3

from argparse import ArgumentParser
import gatt.gatt_linux
import logging
import sys
import random
import time

from homekit.protocol.opcodes import HapBleOpCodes
from homekit.controller import Controller
from homekit.model.services.service_types import ServicesTypes
from homekit.model.characteristics.characteristic_types import CharacteristicsTypes
from homekit.protocol.statuscodes import HapBleStatusCodes
from homekit.protocol.tlv import TLV

from staging.version import VERSION
from staging.tools import find_characteristic, setup_logging, LoggingDevice


def parse_read_response(data, expected_tid):
    # parse header and check stuff
    logging.debug('parse sig read response %s', bytes([int(a) for a in data]).hex())

    # handle the header data
    cf = data[0]
    logging.debug('control field %d', cf)
    tid = data[1]
    logging.debug('transaction id %d (expected was %d)', tid, expected_tid)
    status = data[2]
    logging.debug('status code %d (%s)', status, HapBleStatusCodes[status])
    assert cf == 0x02
    assert tid == expected_tid
    assert status == HapBleStatusCodes.SUCCESS

    # get body length
    length = int.from_bytes(data[3:5], byteorder='little')
    logging.debug('expected body length %d (got %d)', length, len(data[5:]))

    # parse tlvs and analyse information
    tlv = TLV.decode_bytes(data[5:])
    print(TLV.to_string(tlv))


if __name__ == '__main__':
    arg_parser = ArgumentParser(description="GATT Connect Demo")
    arg_parser.add_argument('--adapter', action='store', dest='adapter', default='hci0')
    arg_parser.add_argument('--log', action='store', dest='loglevel')
    arg_parser.add_argument('-f', action='store', required=True, dest='file', help='HomeKit pairing data file')
    arg_parser.add_argument('-a', action='store', required=True, dest='alias', help='alias for the pairing')
    args = arg_parser.parse_args()

    setup_logging(args.loglevel)

    logging.debug('running version: %s', VERSION)
    logging.debug('using adapter %s', args.adapter)

    controller = Controller()
    try:
        controller.load_data(args.file)
    except Exception as e:
        print(e)
        sys.exit(-1)

    if args.alias not in controller.get_pairings():
        print('"{a}" is no known alias'.format(a=args.alias))
        sys.exit(-1)

    pairing_data = controller.pairings[args.alias].pairing_data
    mac_address = pairing_data['AccessoryMAC']

    manager = gatt.DeviceManager(adapter_name=args.adapter)
    device = LoggingDevice(manager=manager, mac_address=mac_address)
    logging.debug('connecting to device')
    device.connect()
    logging.debug('connected to device')

    feature_char, feature_char_id = find_characteristic(device,
                                                        ServicesTypes.PAIRING_SERVICE,
                                                        CharacteristicsTypes.PAIRING_FEATURES)

    if not feature_char:
        print('features characteristic not found')
        sys.exit(-1)

    transaction_id = random.randrange(0, 255)

    data = bytearray([0x00, HapBleOpCodes.CHAR_READ, transaction_id])
    data.extend(feature_char_id.to_bytes(length=2, byteorder='little'))
    result = feature_char.write_value(value=data)
    logging.debug('write resulted in: %s', result)

    data = []
    while len(data) == 0:
        time.sleep(1)
        logging.debug('reading characteristic')
        data = feature_char.read_value()
    resp_data = [b for b in data]
    logging.debug('read: %s', bytearray(resp_data).hex())
    parse_read_response(resp_data, transaction_id)
    # 02 92 00 0300 010101