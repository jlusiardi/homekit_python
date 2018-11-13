#!/usr/bin/env python3

import gatt.gatt_linux
from argparse import ArgumentParser
from homekit.protocol.tlv import TLV
from homekit.model.services.service_types import ServicesTypes
from homekit.model.characteristics.characteristic_types import CharacteristicsTypes
import struct
import logging
import random
import uuid
from homekit.protocol import perform_pair_setup
from homekit.protocol.opcodes import HapBleOpCodes


class ResolvingManager(gatt.gatt_linux.DeviceManager):
    def __init__(self, adapter_name, mac):
        self.mac = mac
        gatt.gatt_linux.DeviceManager.__init__(self, adapter_name=adapter_name)

    def device_discovered(self, device):
        logging.debug('discovered %s', device.mac_address)
        if device.mac_address == self.mac:
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


def create_ble_pair_setup_write(characteristic, char_id):
    def write(request):
        logging.debug('entering write function')
        request_tlv = TLV.encode_list([
            (0x09, bytearray(b'\x01')),
            (0x01, request)
        ])
        t_id = random.randrange(0,255)
        data = bytearray([0x00, HapBleOpCodes.CHAR_WRITE, t_id])
        for b in char_id.to_bytes(length=2, byteorder='little'):
            data.append(b)
        for b in len(request_tlv).to_bytes(length=2, byteorder='little'):
            data.append(b)
        for b in request_tlv:
            data.append(b)
        logging.debug('sent %s', bytes(data).hex())
        characteristic.write_value(value=data)
        data = []
        while len(data) == 0:
            logging.debug('reading characteristic')
            data = characteristic.read_value()
        resp_data = [b for b in data]
        logging.debug('control field: {c:x}, tid: {t:x}, status: {s:x}'.format(c=resp_data[0], t=resp_data[1], s=resp_data[2]))
        logging.debug('received %s', bytes(resp_data).hex())
        resp_tlv = TLV.decode_bytes(bytes([int(a) for a in resp_data[5:]]))
        result = TLV.decode_bytes(resp_tlv[0][1])
        logging.debug('leaving write function')
        return result
    return write


def write(tlv_bytes, t_id, char_id):
    request_tlv = TLV.encode_list([
        (0x09, bytearray(b'\x01')),
        (0x01, tlv_bytes)
    ])
    data = bytearray([0x00, 0x02, t_id])
    for b in char_id.to_bytes(length=2, byteorder='little'):
        data.append(b)
    for b in len(request_tlv).to_bytes(length=2, byteorder='little'):
        data.append(b)
    for b in request_tlv:
        data.append(b)
    # \x00 - Controlfield
    # \x02 - HAP PDU Type
    # \x2A - TID
    # \x0A\x00
    # \x06\x00
    # \x06\x01\x01\x00\x01\x01'
    # \x00\x02\x2A\x00\x0A\x00\x06\x06\x01\x01\x00\x01\x01
    pair_setup_char.write_value(value=data)
    data = pair_setup_char.read_value()
    resp_data = [b for b in data]
    # 02 -- control field
    # 2a -- tid
    # 00 -- success
    # 9d -- param tlv
    # 01 -- value
    # 01 ff 06010203ff75b279ae6989ff814ea10d9f1f6d1112cea842fbd7c609de3d097a3ef7609d01b0334a23378be483518d7c66f2698819c2932fc72210c771f895f52d1fcadddfb3bf00e9c8408d6a30828c8710ab956bf26509c6301582d37a4c72cc8ab56bbaf080864625c5145892749b715bd24a705e891355859134fde37633dd77e287c7cc435b65046ec4a287ccc3fefa6a4ff0419a96b508d9de029c75ed98da80b71789edbda742ea8bbc6460065071a02c43517f203ff6c1d18f7fee5cebe2f7065bcded4c0dd746c3e6f193bd16713fe950e016b7ccda77cd4d8c69e135805989eabd0beb95e7a948f6a0aa1b18bf1b2fccc2538571673a62fa80b7
    # 01 9a 30154d109303813b1181bb8ae099d45ba5be0bf92e920b9711c8ee690c35dfe379165de1e94b8cc3f89648be2f8728c16e72b246884983620f1c573e8ab7a909792a8b0df4da5d24bec2a73f8906d380ee4a77efe020763e45438693754dfa76534a78d2ffc4e527de7bc9474791b6264b467d1535b47b9e00c41a417513477351fc8ef52fcd9479021085cf5244d19be348a4384c3fd777c704
    # inner tlv
    # 06 01 02 - M2
    # below: public key
    # 03 ff 75b279ae6989ff814ea10d9f1f6d1112cea842fbd7c609de3d097a3ef7609d01b0334a23378be483518d7c66f2698819c2932fc72210c771f895f52d1fcadddfb3bf00e9c8408d6a30828c8710ab956bf26509c6301582d37a4c72cc8ab56bbaf080864625c5145892749b715bd24a705e891355859134fde37633dd77e287c7cc435b65046ec4a287ccc3fefa6a4ff0419a96b508d9de029c75ed98da80b71789edbda742ea8bbc6460065071a02c43517f203ff6c1d18f7fee5cebe2f7065bcded4c0dd746c3e6f193bd16713fe950e016b7ccda77cd4d8c69e135805989eabd0beb95e7a948f6a0aa1b18bf1b2fccc2538571673a62fa80b730154d1093
    # 03 81 3b1181bb8ae099d45ba5be0bf92e920b9711c8ee690c35dfe379165de1e94b8cc3f89648be2f8728c16e72b246884983620f1c573e8ab7a909792a8b0df4da5d24bec2a73f8906d380ee4a77efe020763e45438693754dfa76534a78d2ffc4e527de7bc9474791b6264b467d1535b47b9e00c41a417513477351fc8ef52fcd9479
    # below: salt
    # 02 10 85cf5244d19be348a4384c3fd777c704
    resp_tlv = TLV.decode_bytes(bytes([int(a) for a in resp_data[5:]]))
    return TLV.decode_bytes(resp_tlv[0][1])


if __name__ == '__main__':
    arg_parser = ArgumentParser(description="GATT Connect Demo")
    arg_parser.add_argument('mac_address', help="MAC address of device to connect")
    arg_parser.add_argument('--adapter', action='store', dest='adapter', default='hci0')
    arg_parser.add_argument('--log', action='store', dest='loglevel')
    arg_parser.add_argument('-p', action='store', required=True, dest='pin', help='HomeKit configuration code')
    args = arg_parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(filename)s:%(lineno)d %(levelname)s %(message)s')
    if args.loglevel:
        getattr(logging, args.loglevel.upper())
        numeric_level = getattr(logging, args.loglevel.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % args.loglevel)
        logging.getLogger().setLevel(numeric_level)

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
        if CharacteristicsTypes.get_short(CharacteristicsTypes.PAIR_SETUP) == CharacteristicsTypes.get_short(characteristic.uuid.upper()):
            pair_setup_char = characteristic
        if CharacteristicsTypes.get_short(CharacteristicsTypes.PAIR_VERIFY) == CharacteristicsTypes.get_short(characteristic.uuid.upper()):
            pair_verify_char = characteristic
    logging.debug('setup char: %s %s', pair_setup_char, pair_setup_char.service.device)
    logging.debug('verify char: %s', pair_verify_char)

    char_id = 10 # read manually
    t_id = 42 # defined

    # # page 111
    # request_tlv = TLV.encode_list([
    #     (TLV.kTLVType_State, TLV.M1),
    #     (TLV.kTLVType_Method, TLV.PairSetup)
    # ])
    #
    # response_tlv = write(request_tlv, t_id, char_id)
    #
    # logging.debug('response TLV: %s', response_tlv)
    # logging.debug('step: %s', response_tlv[0])
    # logging.debug('pub key: %s', response_tlv[1])
    # logging.debug('salt: %s', response_tlv[2])
    write_fun = create_ble_pair_setup_write(pair_setup_char, char_id)
    pairing = perform_pair_setup(args.pin, str(uuid.uuid4()), write_fun)
    print(pairing)
