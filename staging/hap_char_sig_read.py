#!/usr/bin/env python3

import gatt.gatt_linux
from argparse import ArgumentParser
import homekit.protocol.tlv
from homekit.model.services.service_types import ServicesTypes
from homekit.model.characteristics.characteristic_types import CharacteristicsTypes
from homekit.protocol.tlv import TLV
from homekit.protocol.opcodes import HapBleOpCodes

import struct
import logging
import json


CharacteristicInstanceID='dc46f0fe-81d2-4616-b5d9-6abdd796939a'


# https://developer.nordicsemi.com/nRF5_SDK/nRF51_SDK_v4.x.x/doc/html/group___b_l_e___g_a_t_t___c_p_f___f_o_r_m_a_t_s.html
characteristic_formats = {
    0x01: 'bool',
    0x04: 'uint8',
    0x08: 'uint32',
    0x10: 'int32',
    0x19: 'utf-8',
    0x1b: 'struct'
}

# https://www.bluetooth.com/specifications/assigned-numbers/units
characteristic_units = {
    0x2700: 'none',
    0x27ad: 'percentage',
}


def parse_sig_read_response(data, tid):
    # parse header and check stuff
    logging.debug('parse sig read response %s', bytes([int(a) for a in data]).hex())

    # get body length
    length = int.from_bytes(data[3:5], byteorder='little')
    tlv = homekit.protocol.tlv.TLV.decode_bytes(data[5:])

    # chr type
    chr_type = [int(a) for a in data[7:23]]
    chr_type.reverse()
    chr_type = ''.join('%02x' % b for b in chr_type)

    svc_id = int.from_bytes(data[25:27], byteorder='little')

    svc_type = [int(a) for a in data[29:45]]
    svc_type.reverse()
    svc_type = ''.join('%02x' % b for b in svc_type)

    chr_prop = None
    desc = ''
    format = ''
    range = None
    step = None
    for t in tlv:
        if t[0] == TLV.kTLVHAPParamHAPCharacteristicPropertiesDescriptor:
            chr_prop_int = int.from_bytes(t[1], byteorder='little')
            chr_prop = [int(a) for a in t[1]]
            chr_prop.reverse()
            chr_prop = ''.join('%02x' % b for b in chr_prop)
        if t[0] == TLV.kTLVHAPParamGATTUserDescriptionDescriptor:
            desc = t[1].decode()
        if t[0] == TLV.kTLVHAPParamHAPValidValuesDescriptor:
            print('valid values', t[1])
        if t[0] == TLV.kTLVHAPParamHAPValidValuesRangeDescriptor:
            print('valid values range', t[1])
        if t[0] == TLV.kTLVHAPParamGATTPresentationFormatDescriptor:
            unit_bytes = t[1][2:4]
            unit_bytes.reverse()
            format = characteristic_formats.get(int(t[1][0]), 'unknown')
            unit = characteristic_units.get(int.from_bytes(unit_bytes, byteorder='big'), 'unknown')
            # print('format data', t[1].hex())
            # print('\tFormat', characteristic_formats.get(int(t[1][0]), 'unknown'))
            # print('\tExponent', int(t[1][1]))
            # print('\tUnit', characteristic_units.get(int.from_bytes(unit_bytes, byteorder='big'), 'unknown'))
            # print('\tNamespace', int(t[1][4]))
            # print('\tDescription', t[1][5:].hex())
        if t[0] == TLV.kTLVHAPParamGATTValidRange:
            # print('range', t[1])
            # print(type(t[1]), format)
            lower = None
            upper = None
            if format == 'int32':
                (lower, upper) = struct.unpack('ii', t[1])
            if format == 'uint8':
                (lower, upper) = struct.unpack('BB', t[1])
            # l = len(t[1])
            # lower = t[1][:int(l/2)]
            # upper = t[1][int(l/2):]
            # print(lower, upper)
            range = (lower, upper)
        if t[0] == TLV.kTLVHAPParamHAPStepValueDescriptor:
            # print('step', t[1])
            step = None
            if format == 'int32':
                step = struct.unpack('i', t[1])[0]
            if format == 'uint8':
                step = struct.unpack('B', t[1])[0]

    # print('\t\t\t', 'chr_type', chr_type, 'svc_id', svc_id, 'svc_type', svc_type, 'chr_prop', chr_prop, 'desc >', desc, '<')

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

    return {'description': desc, 'perms': perms, 'format': format, 'unit': unit, 'range': range, 'step': step}


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
        logging.debug('stopped manager')

        self.a_data = {
            'services': []
        }
        for service in self.services:
            logging.debug('found service with UUID %s (%s)', service.uuid, ServicesTypes.get_short(service.uuid.upper()))
            s_data = {
                'sid': None,
                'type': service.uuid.upper(),
                'characteristics': []
            }
            self.a_data['services'].append(s_data)
            for characteristic in service.characteristics:
                logging.debug('\tfound characteristic with UUID %s (%s)', characteristic.uuid, CharacteristicsTypes.get_short(characteristic.uuid.upper()))

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
                    s_data['characteristics'].append(c_data)
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
                        tid = 42
                        characteristic.write_value([0x00, 0x01, tid, v[0], v[1]])
                        d = parse_sig_read_response(characteristic.read_value(), tid)
                        for k in d:
                            c_data[k] = d[k]

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
    logging.debug('discovered')

    manager = gatt.DeviceManager(adapter_name=args.adapter)
    device = AnyDevice(manager=manager, mac_address=args.mac_address)
    logging.debug('connecting to device')
    device.connect()
    logging.debug('connected to device')

    try:
        logging.debug('start manager')
        manager.run()
    except:
        device.disconnect()

    print('-' * 20, 'human readable', '-' * 20)
    for service in device.a_data['services']:
        s_type = service['type']
        s_iid = service['sid']
        s_uuid = service['type']
        print('{iid}: >{stype}< ({uuid})'.format(uuid=s_uuid, iid=s_iid, stype=ServicesTypes.get_short(s_type)))

        for characteristic in service['characteristics']:
            c_iid = characteristic['cid']
            value = characteristic.get('value', '')
            c_type = characteristic['type']
            perms = ','.join(characteristic['perms'])
            desc = characteristic.get('description', '')
            c_type = CharacteristicsTypes.get_short(c_type)
            print('  {aid}.{iid}: {value} ({description}) >{ctype}< [{perms}]'.format(aid=s_iid,
                                                                                      iid=c_iid,
                                                                                      value=value,
                                                                                      ctype=c_type,
                                                                                      perms=perms,
                                                                                      description=desc))

    print('-' * 20, 'json', '-' * 20)
    json_services = []
    for service in device.a_data['services']:
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
                'iid': characteristic['cid'],
                'value': characteristic.get('value', ''),
                'perms': characteristic['perms'],
                'format': characteristic['format'],
                'unit': characteristic['unit'],
                'range': str(characteristic['range']),
                'step': str(characteristic['step']),
            }
            json_characteristics.append(json_characteristic)
        json_services.append(json_service)
    json_data = [{'aid':1,'services': json_services}]
    print(json.dumps(json_data, indent=4))
