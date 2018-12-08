#!/usr/bin/env python3

import logging
import random
import sys
import time
from argparse import ArgumentParser

import gatt.gatt_linux
from homekit.controller import Controller
from homekit.model.characteristics.characteristic_types import CharacteristicsTypes
from homekit.model.services.service_types import ServicesTypes
from homekit.protocol.opcodes import HapBleOpCodes
from staging.tools import find_characteristic, setup_logging, LoggingDevice, parse_read_response
from staging.version import VERSION
# imports for crypto
from homekit.protocol import get_session_keys
from homekit.crypto.chacha20poly1305 import chacha20_aead_encrypt
from staging.hap_pair import create_ble_pair_setup_write

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
    device = LoggingDevice(manager=manager, mac_address=mac_address, managed=False)
    logging.debug('connecting to device')
    device.connect()
    logging.debug('connected to device')

    pair_verify_char, pair_verify_char_id = find_characteristic(device,
                                                                ServicesTypes.PAIRING_SERVICE,
                                                                CharacteristicsTypes.PAIR_VERIFY)

    if not pair_verify_char:
        print('verify characteristic not found')
        sys.exit(-1)

    write_fun = create_ble_pair_setup_write(pair_verify_char, pair_verify_char_id)
    c2a_key, a2c_key = get_session_keys(None, pairing_data, write_fun)
    logging.debug('keys: \n\t\tc2a: %s\n\t\ta2c: %s', c2a_key.hex(), a2c_key.hex())

    read_char, read_char_id = find_characteristic(device,
                                                  ServicesTypes.ACCESSORY_INFORMATION_SERVICE,
                                                  CharacteristicsTypes.NAME)

    if not read_char:
        print('name characteristic not found')
        sys.exit(-1)

    print(read_char.descriptors[0].read_value())

    body = bytearray([])
    transaction_id = random.randrange(0, 255)
    data = bytearray([0x00, HapBleOpCodes.CHAR_READ, transaction_id])
    data.extend(read_char_id.to_bytes(length=2, byteorder='little'))
    data.extend(len(body).to_bytes(length=2, byteorder='little'))
    logging.debug('unencrypted: %s', data.hex())

    # crypt it
    c2a_counter = 0
    cnt_bytes = c2a_counter.to_bytes(8, byteorder='little')
    len_bytes = len(data).to_bytes(2, byteorder='little')
    cipher_and_mac = chacha20_aead_encrypt(len_bytes, c2a_key, cnt_bytes, bytes([0, 0, 0, 0]), data)
    logging.debug('cipher: %s mac: %s', cipher_and_mac[0].hex(), cipher_and_mac[1].hex())
    cipher_and_mac[0].extend(cipher_and_mac[1])
    data=cipher_and_mac[0]
    logging.debug('encrypted: %s', data.hex())

    result = read_char.write_value(value=data)
    logging.debug('write resulted in: %s', result)

    print(device.is_connected())
    data = []
    while len(data) == 0:
        time.sleep(1)
        logging.debug('reading characteristic')
        data = read_char.read_value()
    resp_data = [b for b in data]
    logging.debug('read: %s', bytearray(resp_data).hex())
    parse_read_response(resp_data, transaction_id)