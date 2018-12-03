#!/usr/bin/env python3

from argparse import ArgumentParser
import gatt.gatt_linux
import logging
import sys
import random
import time

from staging.hap_pair import AnyDevice, create_ble_pair_setup_write, ResolvingManager
from staging.hap_char_sig_read import CharacteristicInstanceID

from homekit.controller import Controller
from homekit.model.services.service_types import ServicesTypes
from homekit.model.characteristics.characteristic_types import CharacteristicsTypes
from homekit.protocol import get_session_keys
from homekit.protocol.tlv import TLV
from homekit.crypto.chacha20poly1305 import chacha20_aead_encrypt, chacha20_aead_decrypt
from homekit.protocol.opcodes import HapBleOpCodes
from staging.version import VERSION


if __name__ == '__main__':
    arg_parser = ArgumentParser(description="GATT Connect Demo")
    arg_parser.add_argument('--adapter', action='store', dest='adapter', default='hci0')
    arg_parser.add_argument('--log', action='store', dest='loglevel')
    arg_parser.add_argument('-f', action='store', required=True, dest='file', help='HomeKit pairing data file')
    arg_parser.add_argument('-a', action='store', required=True, dest='alias', help='alias for the pairing')
    args = arg_parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(filename)s:%(lineno)04d %(levelname)s %(message)s')
    if args.loglevel:
        getattr(logging, args.loglevel.upper())
        numeric_level = getattr(logging, args.loglevel.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % args.loglevel)
        logging.getLogger().setLevel(numeric_level)

    logging.debug('running version: %s', VERSION)

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

    # logging.debug('using adapter %s', args.adapter)
    # manager = ResolvingManager(adapter_name=args.adapter, mac=mac_address)
    # manager.start_discovery()
    # manager.run()

    manager = gatt.DeviceManager(adapter_name=args.adapter)
    device = AnyDevice(manager=manager, mac_address=mac_address)
    logging.debug('connecting to device')
    device.connect()
    logging.debug('connected to device')
    # manager.run()

    pairing_service = None
    logging.debug('services: %s', device.services)
    for service in device.services:
        if ServicesTypes.get_short(ServicesTypes.PAIRING_SERVICE) == ServicesTypes.get_short(service.uuid.upper()):
            pairing_service = service
            break
    logging.debug('Pairing Service: %s', pairing_service)

    pair_verify_char = None
    for characteristic in pairing_service.characteristics:
        logging.debug('char: %s %s', characteristic.uuid, CharacteristicsTypes.get_short(characteristic.uuid.upper()))
        if CharacteristicsTypes.get_short(CharacteristicsTypes.PAIR_VERIFY) == CharacteristicsTypes.get_short(
                characteristic.uuid.upper()):
            pair_verify_char = characteristic
            for descriptor in characteristic.descriptors:
                value = descriptor.read_value()
                if descriptor.uuid == CharacteristicInstanceID:
                    cid = int.from_bytes(value, byteorder='little')
                    pair_verify_char_id = cid
    logging.debug('verify char: %s %s', pair_verify_char, pair_verify_char.service.device)

    t_id = random.randrange(0, 255)

    write_fun = create_ble_pair_setup_write(device, pair_verify_char, pair_verify_char_id)
    c2a_key, a2c_key = get_session_keys(None, pairing_data, write_fun)
    logging.debug('keys: %s %s', c2a_key.hex(), a2c_key.hex())

    info_service = None
    logging.debug('services: %s', device.services)
    for service in device.services:
        if ServicesTypes.get_short(ServicesTypes.ACCESSORY_INFORMATION) == ServicesTypes.get_short(service.uuid.upper()):
            info_service = service
            break
    logging.debug('Info Service: %s', info_service)

    name_char = None
    name_char_id = None
    for characteristic in info_service.characteristics:
        logging.debug('char: %s %s', characteristic.uuid, CharacteristicsTypes.get_short(characteristic.uuid.upper()))
        if CharacteristicsTypes.get_short(CharacteristicsTypes.IDENTIFY) == CharacteristicsTypes.get_short(
                characteristic.uuid.upper()):
            name_char = characteristic
            for descriptor in characteristic.descriptors:
                value = descriptor.read_value()
                if descriptor.uuid == CharacteristicInstanceID:
                    cid = int.from_bytes(value, byteorder='little')
                    name_char_id = cid
    logging.debug('name char: %s %s', name_char, name_char.service.device)

    # construct hap characteristic read procedure
    transaction_id = random.randrange(0, 255)
    data = bytearray([0x00, HapBleOpCodes.CHAR_READ, transaction_id])
    data.extend(name_char_id.to_bytes(length=2, byteorder='little'))
    logging.debug('read request %s (tid is %s)', data.hex(), t_id)

    # crypt it
    # c2a_counter = 0
    # cnt_bytes = c2a_counter.to_bytes(8, byteorder='little')
    # len_bytes = len(data).to_bytes(2, byteorder='little')
    # cipher_and_mac = chacha20_aead_encrypt(len_bytes, c2a_key, cnt_bytes, bytes([0, 0, 0, 0]), data)
    # cipher_and_mac[0].extend(cipher_and_mac[1])
    # data = cipher_and_mac[0]
    # logging.debug('cipher and mac %s', cipher_and_mac[0].hex())

    # write the crypted data to the characteristic
    name_char.write_value(data)

    data = []
    while not data or len(data) == 0:
        time.sleep(1)

        data = characteristic.read_value()
        logging.debug('reading characteristic %s', data)
    resp_data = [b for b in data]

    #
    # request_tlv = TLV.encode_list([(1, cipher_and_mac[0]),(16, cipher_and_mac[1]) ])
    # logging.debug('sent %s', request_tlv.hex())
    #
    # request_tlv = TLV.encode_list([
    #     (TLV.kTLVHAPParamValue, request_tlv)
    # ])
    #
    # transaction_id = random.randrange(0, 255)
    # data = bytearray([0x00, HapBleOpCodes.CHAR_WRITE, transaction_id])
    # data.extend(identify_char_id.to_bytes(length=2, byteorder='little'))
    # data.extend(len(request_tlv).to_bytes(length=2, byteorder='little'))
    # data.extend(request_tlv)
    # logging.debug('sent %s', bytes(data).hex())
    # characteristic.write_value(value=data)
    #
    # data = []
    # while len(data) == 0:
    #     time.sleep(1)
    #     logging.debug('reading characteristic')
    #     data = characteristic.read_value()
    # resp_data = [b for b in data]
