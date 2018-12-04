#!/usr/bin/env python3

import gatt.gatt
from argparse import ArgumentParser
import homekit.protocol.tlv
from homekit.model.services.service_types import ServicesTypes
from homekit.model.characteristics.characteristic_types import CharacteristicsTypes
from homekit.model.characteristics.characteristic_formats import BleCharacteristicFormats
from homekit.model.characteristics.characteristic_units import BleCharacteristicUnits
from staging.version import VERSION

from homekit.protocol.tlv import TLV
from homekit.protocol.opcodes import HapBleOpCodes
from homekit.protocol.statuscodes import HapBleStatusCodes

import struct
import logging
import json
import random
import uuid

from staging.tools import CharacteristicInstanceID, setup_logging, ResolvingManager


def parse_sig_read_response(data, expected_tid):
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
    tlv = homekit.protocol.tlv.TLV.decode_bytes(data[5:])

    description = ''
    characteristic_format = ''
    characteristic_range = None
    characteristic_step = None
    for t in tlv:
        if t[0] == TLV.kTLVHAPParamCharacteristicType:
            chr_type = [int(a) for a in t[1]]
            chr_type.reverse()
            chr_type = str(uuid.UUID(''.join('%02x' % b for b in chr_type)))
        if t[0] == TLV.kTLVHAPParamServiceInstanceId:
            svc_id = int.from_bytes(t[1], byteorder='little')
        if t[0] == TLV.kTLVHAPParamServiceType:
            svc_type = [int(a) for a in t[1]]
            svc_type.reverse()
            svc_type = str(uuid.UUID(''.join('%02x' % b for b in svc_type)))
        if t[0] == TLV.kTLVHAPParamHAPCharacteristicPropertiesDescriptor:
            chr_prop_int = int.from_bytes(t[1], byteorder='little')
        if t[0] == TLV.kTLVHAPParamGATTUserDescriptionDescriptor:
            description = t[1].decode()
        if t[0] == TLV.kTLVHAPParamHAPValidValuesDescriptor:
            print('valid values', t[1])
        if t[0] == TLV.kTLVHAPParamHAPValidValuesRangeDescriptor:
            print('valid values range', t[1])
        if t[0] == TLV.kTLVHAPParamGATTPresentationFormatDescriptor:
            unit_bytes = t[1][2:4]
            unit_bytes.reverse()
            characteristic_format = BleCharacteristicFormats.get(int(t[1][0]), 'unknown')
            unit = BleCharacteristicUnits.get(int.from_bytes(unit_bytes, byteorder='big'), 'unknown')
        if t[0] == TLV.kTLVHAPParamGATTValidRange:
            logging.debug('range: %s', t[1].hex())
            lower = None
            upper = None
            if characteristic_format == 'int32' or characteristic_format == 'int':
                (lower, upper) = struct.unpack('ii', t[1])
            if characteristic_format == 'uint8':
                (lower, upper) = struct.unpack('BB', t[1])
            if characteristic_format == 'float':
                (lower, upper) = struct.unpack('ff', t[1])
            # TODO include all formats!
            characteristic_range = (lower, upper)
        if t[0] == TLV.kTLVHAPParamHAPStepValueDescriptor:
            characteristic_step = None
            if characteristic_format == 'int32':
                characteristic_step = struct.unpack('i', t[1])[0]
            if characteristic_format == 'uint8':
                characteristic_step = struct.unpack('B', t[1])[0]
            # TODO include all formats!

    # parse permissions
    # TODO refactor!
    perms = []
    if (chr_prop_int & 0x0001) > 0:
        perms.append('r')
    if (chr_prop_int & 0x0002) > 0:
        perms.append('w')
    if (chr_prop_int & 0x0004) > 0:
        perms.append('aad')
    if (chr_prop_int & 0x0008) > 0:
        perms.append('tw')
    if (chr_prop_int & 0x0010) > 0:
        perms.append('pr')
    if (chr_prop_int & 0x0020) > 0:
        perms.append('pw')
    if (chr_prop_int & 0x0040) > 0:
        perms.append('hd')
    if (chr_prop_int & 0x0080) > 0:
        perms.append('evc')
    if (chr_prop_int & 0x0100) > 0:
        perms.append('evd')

    result = {'description': description, 'perms': perms, 'format': characteristic_format, 'unit': unit,
              'range': characteristic_range, 'step': characteristic_step,
              'type': chr_type, 'service_id': svc_id, 'service_type': svc_type}
    logging.debug('result: %s', str(result))

    return result


class ServicesResolvingDevice(gatt.gatt.Device):
    def __init__(self, mac_address, manager, managed=True):
        gatt.gatt.Device.__init__(self, mac_address, manager, managed)
        self.resolved_data = None

    def services_resolved(self):
        super().services_resolved()
        logging.debug('resolved %d services', len(self.services))
        self.manager.stop()
        logging.debug('stopped manager')

        self.resolved_data = {
            'services': []
        }
        for service in self.services:
            logging.debug('found service with UUID %s (%s)', service.uuid,
                          ServicesTypes.get_short(service.uuid.upper()))
            s_data = {
                'sid': None,
                'type': service.uuid.upper(),
                'characteristics': []
            }
            for characteristic in service.characteristics:
                logging.debug('\tfound characteristic with UUID %s (%s)', characteristic.uuid,
                              CharacteristicsTypes.get_short(characteristic.uuid.upper()))

                if characteristic.uuid.upper() == CharacteristicsTypes.SERVICE_INSTANCE_ID:
                    sid = int.from_bytes(characteristic.read_value(), byteorder='little')
                    logging.debug('\t\tread service id %d', sid)
                    s_data['sid'] = sid
                else:
                    c_data = {
                        'cid': None,
                        'type': characteristic.uuid.upper(),
                        'perms': []
                    }
                    cid = None
                    for descriptor in characteristic.descriptors:
                        value = descriptor.read_value()
                        if descriptor.uuid == CharacteristicInstanceID:
                            cid = int.from_bytes(value, byteorder='little')
                            logging.debug('\t\tread characteristic id %d', cid)
                            c_data['cid'] = cid
                        else:
                            # print('\t\t', 'D', descriptor.uuid, value)
                            pass

                    if cid:
                        v = cid.to_bytes(length=2, byteorder='little')
                        tid = random.randrange(0, 255)
                        characteristic.write_value([0x00, HapBleOpCodes.CHAR_SIG_READ, tid, v[0], v[1]])
                        d = parse_sig_read_response(characteristic.read_value(), tid)
                        for k in d:
                            c_data[k] = d[k]
                    if c_data['cid']:
                        s_data['characteristics'].append(c_data)
            if s_data['sid']:
                self.resolved_data['services'].append(s_data)

        logging.debug('data: %s', self.resolved_data)
        logging.debug('disconnecting from device')
        self.disconnect()
        logging.debug('disconnected from device')
        self.manager.stop()
        logging.debug('manager stopped')


if __name__ == '__main__':
    arg_parser = ArgumentParser(description="GATT Connect Demo")
    arg_parser.add_argument('mac_address', help="MAC address of device to connect")
    arg_parser.add_argument('--adapter', action='store', dest='adapter', default='hci0')
    arg_parser.add_argument('--log', action='store', dest='loglevel')
    arg_parser.add_argument('-o', action='store', dest='output', default='compact', choices=['json', 'compact'],
                        help='Specify output format')
    args = arg_parser.parse_args()

    setup_logging(args.loglevel)

    logging.debug('Running version %s', VERSION)
    logging.debug('using adapter %s', args.adapter)
    manager = ResolvingManager(adapter_name=args.adapter, mac=args.mac_address)
    manager.start_discovery()
    manager.run()
    logging.debug('discovered')

    manager = gatt.DeviceManager(adapter_name=args.adapter)
    device = ServicesResolvingDevice(manager=manager, mac_address=args.mac_address)
    logging.debug('connecting to device')
    device.connect()
    logging.debug('connected to device')

    try:
        logging.debug('start manager')
        manager.run()
    except:
        device.disconnect()

    if args.output == 'compact':
        for service in device.resolved_data['services']:
            s_type = service['type'].upper()
            s_iid = service['sid']
            print('{iid}: >{stype}< ({uuid})'.format(uuid=s_type, iid=s_iid, stype=ServicesTypes.get_short(s_type)))

            for characteristic in service['characteristics']:
                c_iid = characteristic['cid']
                value = characteristic.get('value', '')
                c_type = characteristic['type'].upper()
                perms = ','.join(characteristic['perms'])
                desc = characteristic.get('description', '')
                c_type = CharacteristicsTypes.get_short(c_type)
                print('  {aid}.{iid}: {value} ({description}) >{ctype}< [{perms}]'.format(aid=s_iid,
                                                                                          iid=c_iid,
                                                                                          value=value,
                                                                                          ctype=c_type,
                                                                                          perms=perms,
                                                                                          description=desc))

    if args.output == 'json':
        json_services = []
        for service in device.resolved_data['services']:
            json_characteristics = []
            json_service = {
                'type': service['type'],
                'iid': service['sid'],
                'characteristics': json_characteristics
            }
            for characteristic in service['characteristics']:
                json_characteristic = {
                    'type': characteristic['type'],
                    'description': characteristic.get('description', ''),
                    'aid': service['sid'],
                    'iid': characteristic['cid'],
                    'value': characteristic.get('value', ''),
                    'perms': characteristic['perms'],
                    'format': characteristic.get('format', 'missing'),
                    'unit': characteristic.get('unit', 'missing'),
                    'range': str(characteristic.get('range', 'missing')),
                    'step': str(characteristic.get('step', 'missing')),
                }
                json_characteristics.append(json_characteristic)
            json_services.append(json_service)
        json_data = [{'aid': 1, 'services': json_services}]
        print(json.dumps(json_data, indent=4))
