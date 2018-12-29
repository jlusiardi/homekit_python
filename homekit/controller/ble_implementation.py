import time
import logging
import random
import sys
import uuid
import struct
import dbus.exceptions
from distutils.util import strtobool

from homekit.controller.tools import AbstractPairing
from homekit.exceptions import AccessoryNotFoundError
from homekit.protocol.tlv import TLV
from homekit.model.characteristics import CharacteristicsTypes
from homekit.protocol import get_session_keys
from homekit.protocol.opcodes import HapBleOpCodes
from homekit.protocol.statuscodes import HapBleStatusCodes
from homekit.model.services.service_types import ServicesTypes
from homekit.crypto import chacha20_aead_decrypt, chacha20_aead_encrypt
from homekit.model.characteristics.characteristic_formats import BleCharacteristicFormats, CharacteristicFormats
from homekit.model.characteristics.characteristic_units import BleCharacteristicUnits
from homekit.exceptions import FormatError

import staging.gatt

# the uuid of the ble descriptors that hold the characteristic instance id as value (see page 128)
CharacteristicInstanceID = 'dc46f0fe-81d2-4616-b5d9-6abdd796939a'


class BlePairing(AbstractPairing):

    def __init__(self, pairing_data):
        """
        Initialize a Pairing by using the data either loaded from file or obtained after calling
        Controller.perform_pairing().

        :param pairing_data:
        """
        self.pairing_data = pairing_data
        self.session = None

    def close(self):
        pass

    def list_accessories_and_characteristics(self):
        manager = staging.gatt.DeviceManager(adapter_name='hci0')
        device = ServicesResolvingDevice(manager=manager, mac_address=self.pairing_data['AccessoryMAC'])
        device.connect()
        self.pairing_data['accessories'] = device.resolved_data['data']
        return device.resolved_data['data']

    def list_pairings(self):
        pass

    def get_events(self, characteristics, callback_fun, max_events=-1, max_seconds=-1):
        pass

    def identify(self):
        pass

    def get_characteristics(self, characteristics, include_meta=False, include_perms=False, include_type=False,
                            include_events=False):
        """
        This method is used to get the current readouts of any characteristic of the accessory.

        :param characteristics: a list of 2-tupels of accessory id and instance id
        :param include_meta: if True, include meta information about the characteristics. This contains the format and
                             the various constraints like maxLen and so on.
        :param include_perms: if True, include the permissions for the requested characteristics.
        :param include_type: if True, include the type of the characteristics in the result. See CharacteristicsTypes
                             for translations.
        :param include_events: if True on a characteristics that supports events, the result will contain information if
                               the controller currently is receiving events for that characteristic. Key is 'ev'.
        :return: a dict mapping 2-tupels of aid and iid to dicts with value or status and description, e.g.
                 {(1, 8): {'value': 23.42}
                  (1, 37): {'description': 'Resource does not exist.', 'status': -70409}
                 }
        """
        if not self.session:
            self.session = BleSession(self.pairing_data)

        results = {}
        for aid, cid in characteristics:
            fc, fc_id = find_characteristic_by_aid_iid(self.session.device, aid, cid)

            response = self.session.request(fc, fc_id, HapBleOpCodes.CHAR_READ)

            value = self._convert_to_python(aid, cid, response[1]) if 1 in response else None

            results[(aid, cid)] = {
                'value': value
            }

        return results

    def _convert_from_python(self, aid, cid, value):
        char_format = None
        for a in self.pairing_data['accessories']:
            if a['aid'] != int(aid):
                continue

            for s in a['services']:
                for c in s['characteristics']:
                    if c['iid'] == int(cid):
                        char_format = c['format']
                        break
        logging.debug('value: %s format: %s', value, char_format)

        if char_format == CharacteristicFormats.bool:
            try:
                val = strtobool(str(value))
            except ValueError:
                raise FormatError('"{v}" is no valid "{t}"!'.format(v=val, t=char_format))

            value = struct.pack('?', val)
        elif char_format == CharacteristicFormats.int:
            value = struct.pack('i', int(value))
        elif char_format == CharacteristicFormats.float:
            value = struct.pack('f', float(value))

        return value

    def _convert_to_python(self, aid, cid, value):
        char_format = None
        for a in self.pairing_data['accessories']:
            if a['aid'] != int(aid):
                continue

            for s in a['services']:
                for c in s['characteristics']:
                    if c['iid'] == int(cid):
                        char_format = c['format']
                        break
        logging.debug('value: %s format: %s', value.hex(), char_format)

        if char_format == CharacteristicFormats.bool:
            value = struct.unpack('?', value)[0]
        elif char_format == CharacteristicFormats.uint8:
            value = struct.unpack('B', value)[0]
        elif char_format == CharacteristicFormats.uint16:
            value = struct.unpack('H', value)[0]
        elif char_format == CharacteristicFormats.uint32:
            value = struct.unpack('I', value)[0]
        elif char_format == CharacteristicFormats.uint64:
            value = struct.unpack('Q', value)[0]
        elif char_format == CharacteristicFormats.int:
            value = struct.unpack('i', value)[0]
        elif char_format == CharacteristicFormats.float:
            value = struct.unpack('f', value)[0]
        elif char_format == CharacteristicFormats.string:
            value = value.decode('UTF-8')
        else:
            value = value.hex()

        return value

    def put_characteristics(self, characteristics, do_conversion=False):
        """
        Update the values of writable characteristics. The characteristics have to be identified by accessory id (aid),
        instance id (iid). If do_conversion is False (the default), the value must be of proper format for the
        characteristic since no conversion is done. If do_conversion is True, the value is converted.

        :param characteristics: a list of 3-tupels of accessory id, instance id and the value
        :param do_conversion: select if conversion is done (False is default)
        :return: a dict from (aid, iid) onto {status, description}
        :raises FormatError: if the input value could not be converted to the target type and conversion was
                             requested
        """
        if not self.session:
            self.session = BleSession(self.pairing_data)

        for aid, cid, value in characteristics:
            fc, fc_id = find_characteristic_by_aid_iid(self.session.device, aid, cid)

            # TODO convert input value into proper representation for type
            value = TLV.encode_list([(1, self._convert_from_python(aid, cid, value))])
            # value = TLV.encode_list([(1, value)])
            body = len(value).to_bytes(length=2, byteorder='little') + value

            response = self.session.request(
                fc,
                fc_id,
                HapBleOpCodes.CHAR_WRITE,
                body,
            )


class BleSession(object):

    def __init__(self, pairing_data):
        self.pairing_data = pairing_data
        self.c2a_counter = 0
        self.a2c_counter = 0
        self.c2a_key = None
        self.a2c_key = None
        self.device = None
        mac_address = self.pairing_data['AccessoryMAC']

        # TODO specify adapter by config?
        manager = staging.gatt.DeviceManager(adapter_name='hci0')

        self.device = Device(manager=manager, mac_address=mac_address)
        logging.debug('connecting to device')
        self.device.connect()
        logging.debug('connected to device')

        pair_verify_char, pair_verify_char_id = find_characteristic_by_uuid(
            self.device,
            ServicesTypes.PAIRING_SERVICE,
            CharacteristicsTypes.PAIR_VERIFY
        )

        if not pair_verify_char:
            print('verify characteristic not found')
            # TODO Have exception here
            sys.exit(-1)

        write_fun = create_ble_pair_setup_write(pair_verify_char, pair_verify_char_id)
        self.c2a_key, self.a2c_key = get_session_keys(None, self.pairing_data, write_fun)
        logging.debug('keys: \n\t\tc2a: %s\n\t\ta2c: %s', self.c2a_key.hex(), self.a2c_key.hex())

        self.c2a_counter = 0
        self.a2c_counter = 0

    def request(self, feature_char, feature_char_id, op, body=None):
        transaction_id = random.randrange(0, 255)

        data = bytearray([0x00, op, transaction_id])
        data.extend(feature_char_id.to_bytes(length=2, byteorder='little'))

        if body:
            logging.debug('body: %s', body)
            data.extend(body)

        cnt_bytes = self.c2a_counter.to_bytes(8, byteorder='little')
        cipher_and_mac = chacha20_aead_encrypt(bytes(), self.c2a_key, cnt_bytes, bytes([0, 0, 0, 0]), data)
        cipher_and_mac[0].extend(cipher_and_mac[1])
        data = cipher_and_mac[0]
        logging.debug('cipher and mac %s', cipher_and_mac[0].hex())

        result = feature_char.write_value(value=data)
        logging.debug('write resulted in: %s', result)

        self.c2a_counter += 1

        data = []
        while not data or len(data) == 0:
            time.sleep(1)
            logging.debug('reading characteristic')
            data = feature_char.read_value()
        resp_data = bytearray([b for b in data])
        logging.debug('read: %s', bytearray(resp_data).hex())

        data = chacha20_aead_decrypt(bytes(), self.a2c_key, self.a2c_counter.to_bytes(8, byteorder='little'),
                                     bytes([0, 0, 0, 0]), resp_data)

        logging.debug('decrypted: %s', bytearray(data).hex())

        if not data:
            return {}

        # parse header and check stuff
        logging.debug('parse sig read response %s', bytes([int(a) for a in data]).hex())

        # handle the header data
        cf = data[0]
        logging.debug('control field %d', cf)
        tid = data[1]
        logging.debug('transaction id %d (expected was %d)', tid, transaction_id)
        status = data[2]
        logging.debug('status code %d (%s)', status, HapBleStatusCodes[status])
        assert cf == 0x02
        assert tid == transaction_id
        assert status == HapBleStatusCodes.SUCCESS

        self.a2c_counter += 1

        # get body length
        length = int.from_bytes(data[3:5], byteorder='little')
        logging.debug('expected body length %d (got %d)', length, len(data[5:]))

        # parse tlvs and analyse information
        tlv = TLV.decode_bytes(data[5:])
        logging.debug('received TLV: %s', TLV.to_string(tlv))
        return dict(tlv)


def find_characteristic_by_uuid(device, service_uuid, char_uuid):
    """

    :param device:
    :param service_uuid:
    :param char_uuid:
    :return:
    """
    service_found = None
    logging.debug('services: %s', device.services)
    for possible_service in device.services:
        if ServicesTypes.get_short(service_uuid.upper()) == ServicesTypes.get_short(possible_service.uuid.upper()):
            service_found = possible_service
            break
    logging.debug('searched service: %s', service_found)

    if not service_found:
        logging.error('searched service not found.')
        return None, None

    result_char = None
    result_char_id = None
    for characteristic in service_found.characteristics:
        logging.debug('char: %s %s', characteristic.uuid, CharacteristicsTypes.get_short(characteristic.uuid.upper()))
        if CharacteristicsTypes.get_short(char_uuid.upper()) == CharacteristicsTypes.get_short(
                characteristic.uuid.upper()):
            result_char = characteristic
            for descriptor in characteristic.descriptors:
                value = descriptor.read_value()
                if descriptor.uuid == CharacteristicInstanceID:
                    cid = int.from_bytes(value, byteorder='little')
                    result_char_id = cid

    if not result_char:
        logging.error('searched char not found.')
        return None, None

    logging.debug('searched char: %s %s', result_char, result_char_id)
    return result_char, result_char_id


def find_characteristic_by_aid_iid(device, aid, iid):
    """

    :param device:
    :param aid: accessory id
    :param iid: instance id
    :return:
    """
    service_found = None
    logging.debug('services: %s', device.services)
    for possible_service in device.services:
        for characteristic in possible_service.characteristics:
            if characteristic.uuid.upper() == CharacteristicsTypes.SERVICE_INSTANCE_ID:
                sid = int.from_bytes(characteristic.read_value(), byteorder='little')
                logging.debug('%s == %s -> %s (%s, %s)', sid, aid, sid == aid, type(sid), type(aid))
                if aid == sid:
                    service_found = possible_service
                    break
        if service_found:
            break
    logging.debug('searched service: %s', service_found)

    if not service_found:
        logging.error('searched service not found.')
        return None, None

    result_char = None
    result_char_id = None
    for characteristic in service_found.characteristics:
        logging.debug('char: %s %s', characteristic.uuid, CharacteristicsTypes.get_short(characteristic.uuid.upper()))
        for descriptor in characteristic.descriptors:
            value = descriptor.read_value()
            cid = int.from_bytes(value, byteorder='little')
            if iid == cid:
                result_char = characteristic
                result_char_id = cid
                break
        if result_char:
            break

    if not result_char:
        logging.error('searched char not found.')
        return None, None

    logging.debug('searched char: %s %s', result_char, result_char_id)
    return result_char, result_char_id


def create_ble_pair_setup_write(characteristic, characteristic_id):
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


class ResolvingManager(staging.gatt.DeviceManager):
    """
    DeviceManager implementation that stops running after a given device was discovered.
    """
    def __init__(self, adapter_name, mac):
        self.mac = mac
        staging.gatt.DeviceManager.__init__(self, adapter_name=adapter_name)

    def device_discovered(self, device):
        logging.debug('discovered %s', device.mac_address.upper())
        if device.mac_address.upper() == self.mac.upper():
            self.stop()


class Device(staging.gatt.gatt.Device):

    def connect(self):
        super().connect()

        try:
            if not self.services:
                logging.debug('waiting for services to be resolved')
                for i in range(10):
                    if self.is_services_resolved():
                        break
                    time.sleep(1)
                else:
                    raise AccessoryNotFoundError('Unable to resolve device services + characteristics')

                # This is called automatically when the mainloop is running, but we
                # want to avoid running it and blocking for an indeterminate amount of time.
                logging.debug('enumerating resolved services')
                self.services_resolved()
        except dbus.exceptions.DBusException as e:
            raise AccessoryNotFoundError('Unable to resolve device services + characteristics')


class ServicesResolvingDevice(Device):

    def __init__(self, mac_address, manager, managed=True):
        staging.gatt.gatt.Device.__init__(self, mac_address, manager, managed)
        self.resolved_data = None

    def services_resolved(self):
        super().services_resolved()
        logging.debug('resolved %d services', len(self.services))
        self.manager.stop()
        logging.debug('stopped manager')

        self.resolved_data = {
            'data': []
        }
        for service in self.services:
            logging.debug('found service with UUID %s (%s)', service.uuid,
                          ServicesTypes.get_short(service.uuid.upper()))
            s_data = {
                'aid': None,
#                'type': service.uuid.upper(),
                'services': [
                        {
                            'characteristics': [
                            ],
                            'iid': None
                        }
                ]
            }
            
            for characteristic in service.characteristics:
                logging.debug('\tfound characteristic with UUID %s (%s)', characteristic.uuid,
                              CharacteristicsTypes.get_short(characteristic.uuid.upper()))

                if characteristic.uuid.upper() == CharacteristicsTypes.SERVICE_INSTANCE_ID:
                    aid = int.from_bytes(characteristic.read_value(), byteorder='little')
                    logging.debug('\t\tread service id %d', aid)
                    s_data['aid'] = aid
                else:
                    c_data = {
                        'iid': None,
                        'type': characteristic.uuid.upper(),
                        'perms': []
                    }
                    iid = None
                    for descriptor in characteristic.descriptors:
                        value = descriptor.read_value()
                        if descriptor.uuid == CharacteristicInstanceID:
                            iid = int.from_bytes(value, byteorder='little')
                            logging.debug('\t\tread characteristic id %d', iid)
                            c_data['iid'] = iid
                        else:
                            # print('\t\t', 'D', descriptor.uuid, value)
                            pass

                    if iid:
                        v = iid.to_bytes(length=2, byteorder='little')
                        tid = random.randrange(0, 255)
                        characteristic.write_value([0x00, HapBleOpCodes.CHAR_SIG_READ, tid, v[0], v[1]])
                        d = parse_sig_read_response(characteristic.read_value(), tid)
                        for k in d:
                            if k == 'service_type':
                                s_data['services'][0]['type'] = d[k]
                            elif k == 'sid':
                                s_data['services'][0]['iid'] = d[k]
                            else:
                                c_data[k] = d[k]
                    if c_data['iid']:
                        s_data['services'][0]['characteristics'].append(c_data)

            #

            if s_data['aid']:
                self.resolved_data['data'].append(s_data)

        logging.debug('data: %s', self.resolved_data)
        logging.debug('disconnecting from device')
        self.disconnect()
        logging.debug('disconnected from device')
        self.manager.stop()
        logging.debug('manager stopped')


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
    tlv = TLV.decode_bytes(data[5:])

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
              'type': chr_type, 'sid': svc_id, 'service_type': svc_type}
    logging.debug('result: %s', str(result))

    return result
