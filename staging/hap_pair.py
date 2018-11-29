#!/usr/bin/env python3

import gatt.gatt_linux
from argparse import ArgumentParser
import logging
import random
import uuid
import time
import sys

from homekit.protocol.tlv import TLV
from homekit.model.services.service_types import ServicesTypes
from homekit.model.characteristics.characteristic_types import CharacteristicsTypes
from homekit.protocol import perform_pair_setup
from homekit.protocol.opcodes import HapBleOpCodes
from staging.hap_char_sig_read import CharacteristicInstanceID
from homekit.controller import Controller, BlePairing
from staging.version import VERSION


class ResolvingManager(gatt.gatt_linux.DeviceManager):
    def __init__(self, adapter_name, mac):
        self.mac = mac
        gatt.gatt_linux.DeviceManager.__init__(self, adapter_name=adapter_name)

    def device_discovered(self, device):
        logging.debug('discovered %s', device.mac_address)
        if device.mac_address.upper() == self.mac.upper():
            self.stop()


class AnyDevice(gatt.gatt_linux.Device):
    def services_resolved(self):
        super().services_resolved()
        logging.debug('resolved %d services', len(self.services))
        self.manager.stop()

    def characteristic_read_value_failed(self, characteristic, error):
        logging.debug('read failed: %s %s', characteristic, error)

    def characteristic_write_value_succeeded(self, characteristic):
        logging.debug('write success: %s', characteristic)
        self.manager.stop()

    def characteristic_write_value_failed(self, characteristic, error):
        logging.debug('write failed: %s %s', characteristic, error)


def create_ble_pair_setup_write(device, characteristic, characteristic_id):
    def write(request, expected):
        logging.debug('entering write function %s', TLV.to_string(TLV.decode_bytes(request)))
        request_tlv = TLV.encode_list([
            (TLV.kTLVHAPParamParamReturnResponse, bytearray(b'\x01')),
            (TLV.kTLVHAPParamValue, request)
        ])
        transaction_id = random.randrange(0, 255)
        data = bytearray([0x00, HapBleOpCodes.CHAR_WRITE, transaction_id])
        data.extend(characteristic_id.to_bytes(length=2, byteorder='little'))
        data.extend(len(request_tlv).to_bytes(length=2, byteorder='little'))
        data.extend(request_tlv)
        logging.debug('sent %s', bytes(data).hex())
        characteristic.write_value(value=data)
        data = []
        while len(data) == 0:
            time.sleep(1)
            logging.debug('reading characteristic')
            data = characteristic.read_value()
        resp_data = [b for b in data]

        expected_length = int.from_bytes(bytes(resp_data[3:5]), byteorder='little')
        logging.debug(
            'control field: {c:x}, tid: {t:x}, status: {s:x}, length: {l}'.format(c=resp_data[0], t=resp_data[1],
                                                                                  s=resp_data[2], l=expected_length))
        while len(resp_data[3:]) < expected_length:
            time.sleep(1)
            logging.debug('reading characteristic')
            data = characteristic.read_value()
            resp_data.extend([b for b in data])
            logging.debug('data %s of %s', len(resp_data[3:]), expected_length)

        logging.debug('received %s', bytes(resp_data).hex())
        logging.debug('decode %s', bytes(resp_data[5:]).hex())
        resp_tlv = TLV.decode_bytes(bytes([int(a) for a in resp_data[5:]]), expected=[TLV.kTLVHAPParamValue])
        result = TLV.decode_bytes(resp_tlv[0][1], expected)
        logging.debug('leaving write function %s', TLV.to_string(result))
        return result

    return write


if __name__ == '__main__':
    arg_parser = ArgumentParser(description="GATT Connect Demo")
    arg_parser.add_argument('-m', action='store', required=True, dest='mac_address', help="MAC address of device to connect")
    arg_parser.add_argument('--adapter', action='store', dest='adapter', default='hci0')
    arg_parser.add_argument('--log', action='store', dest='loglevel')
    arg_parser.add_argument('-p', action='store', required=True, dest='pin', help='HomeKit configuration code')
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

    controller = Controller()
    try:
        controller.load_data(args.file)
    except Exception as e:
        print(e)
        sys.exit(-1)

    logging.debug('Running version %s', VERSION)
    logging.debug('using adapter %s', args.adapter)
    manager = ResolvingManager(adapter_name=args.adapter, mac=args.mac_address)
    manager.start_discovery()
    manager.run()

    manager = gatt.DeviceManager(adapter_name=args.adapter)
    device = AnyDevice(manager=manager, mac_address=args.mac_address)
    logging.debug('connecting to device')
    device.connect()
    logging.debug('connected to device')
    manager.run()

    pairing_service = None
    for service in device.services:
        if ServicesTypes.get_short(ServicesTypes.PAIRING_SERVICE) == ServicesTypes.get_short(service.uuid.upper()):
            pairing_service = service
            break
    logging.debug('Pairing Service: %s', pairing_service)

    pair_setup_char = None
    pair_verify_char = None
    for characteristic in pairing_service.characteristics:
        logging.debug('char: %s %s', characteristic.uuid, CharacteristicsTypes.get_short(characteristic.uuid.upper()))
        if CharacteristicsTypes.get_short(CharacteristicsTypes.PAIR_SETUP) == CharacteristicsTypes.get_short(
                characteristic.uuid.upper()):
            pair_setup_char = characteristic
            for descriptor in characteristic.descriptors:
                value = descriptor.read_value()
                if descriptor.uuid == CharacteristicInstanceID:
                    cid = int.from_bytes(value, byteorder='little')
                    pair_setup_char_id = cid

        if CharacteristicsTypes.get_short(CharacteristicsTypes.PAIR_VERIFY) == CharacteristicsTypes.get_short(
                characteristic.uuid.upper()):
            pair_verify_char = characteristic
    logging.debug('setup char: %s %s', pair_setup_char, pair_setup_char.service.device)
    logging.debug('verify char: %s', pair_verify_char)

    t_id = random.randrange(0, 255)

    write_fun = create_ble_pair_setup_write(device, pair_setup_char, pair_setup_char_id)
    pairing = perform_pair_setup(args.pin, str(uuid.uuid4()), write_fun)

    pairing['AccessoryMAC'] = args.mac_address
    pairing['Connection'] = 'BLE'

    controller.pairings[args.alias] = BlePairing(pairing)
    controller.save_data(args.file)

    logging.debug('written data to %s using alias %s', args.file, args.alias)


