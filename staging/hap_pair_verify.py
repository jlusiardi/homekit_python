#!/usr/bin/env python3

from argparse import ArgumentParser
import gatt.gatt_linux
import logging
import sys

from staging.hap_pair import create_ble_pair_setup_write

from homekit.controller import Controller
from homekit.model.services.service_types import ServicesTypes
from homekit.model.characteristics.characteristic_types import CharacteristicsTypes
from homekit.protocol import get_session_keys

from staging.version import VERSION
from staging.tools import find_characteristic, setup_logging, LoggingDevice


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

    pair_verify_char, pair_verify_char_id = find_characteristic(device,
                                                                ServicesTypes.PAIRING_SERVICE,
                                                                CharacteristicsTypes.PAIR_VERIFY)

    if not pair_verify_char:
        print('verify characteristic not found')
        sys.exit(-1 )

    write_fun = create_ble_pair_setup_write(pair_verify_char, pair_verify_char_id)
    c2a_key, a2c_key = get_session_keys(None, pairing_data, write_fun)
    logging.debug('keys: \n\t\tc2a: %s\n\t\ta2c: %s', c2a_key.hex(), a2c_key.hex())
