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

__all__ = [
    'Device', 'BlePairing', 'BleSession', 'find_characteristic_by_uuid', 'create_ble_pair_setup_write'
]

import time
import logging
import random
import sys
import uuid
import struct
from distutils.util import strtobool

from homekit.controller.tools import AbstractPairing
from homekit.protocol.tlv import TLV
from homekit.model.characteristics import CharacteristicsTypes
from homekit.protocol import get_session_keys
from homekit.protocol.opcodes import HapBleOpCodes
from homekit.protocol.statuscodes import HapBleStatusCodes
from homekit.model.services.service_types import ServicesTypes
from homekit.crypto import chacha20_aead_decrypt, chacha20_aead_encrypt
from homekit.model.characteristics.characteristic_formats import BleCharacteristicFormats, CharacteristicFormats
from homekit.model.characteristics.characteristic_units import BleCharacteristicUnits
from homekit.exceptions import FormatError, RequestRejected, AccessoryDisconnectedError

from homekit.tools import BLE_TRANSPORT_SUPPORTED

if BLE_TRANSPORT_SUPPORTED:
    from .device import DeviceManager, Device
else:
    # this empty class is required to be inherited by ResolvingManager
    class DeviceManager:
        pass

# the uuid of the ble descriptors that hold the characteristic instance id as value (see page 128)
CharacteristicInstanceID = 'dc46f0fe-81d2-4616-b5d9-6abdd796939a'

logger = logging.getLogger(__name__)


class BlePairing(AbstractPairing):

    def __init__(self, pairing_data, adapter='hci0'):
        """
        Initialize a Pairing by using the data either loaded from file or obtained after calling
        Controller.perform_pairing().

        :param pairing_data:
        """
        self.adapter = adapter
        self.pairing_data = pairing_data
        self.session = None

    def close(self):
        pass

    def list_accessories_and_characteristics(self):
        if 'accessories' in self.pairing_data:
            return self.pairing_data['accessories']

        manager = DeviceManager(self.adapter)
        device = manager.make_device(self.pairing_data['AccessoryMAC'])
        device.connect()
        resolved_data = read_characteristics(device)
        self.pairing_data['accessories'] = resolved_data['data']
        return resolved_data['data']

    def list_pairings(self):
        if not self.session:
            self.session = BleSession(self.pairing_data, self.adapter)
        request_tlv = TLV.encode_list([
            (TLV.kTLVType_State, TLV.M1),
            (TLV.kTLVType_Method, TLV.ListPairings)
        ])
        request_tlv = TLV.encode_list([
            (TLV.kTLVHAPParamParamReturnResponse, bytearray(b'\x01')),
            (TLV.kTLVHAPParamValue, request_tlv)
        ])
        body = len(request_tlv).to_bytes(length=2, byteorder='little') + request_tlv

        cid = -1
        for a in self.pairing_data['accessories']:
            for s in a['services']:
                for c in s['characteristics']:
                    if CharacteristicsTypes.get_short_uuid(c['type'].upper()) == CharacteristicsTypes.PAIRING_PAIRINGS:
                        cid = c['iid']
        fc, _ = self.session.find_characteristic_by_iid(cid)
        response = self.session.request(fc, cid, HapBleOpCodes.CHAR_WRITE, body)
        response = TLV.decode_bytes(response[1])
        tmp = []
        r = {}
        for d in response[1:]:
            if d[0] == TLV.kTLVType_Identifier:
                r = {}
                tmp.append(r)
                r['pairingId'] = d[1].decode()
            if d[0] == TLV.kTLVType_PublicKey:
                r['publicKey'] = d[1].hex()
            if d[0] == TLV.kTLVType_Permissions:
                controller_type = 'regular'
                if d[1] == b'\x01':
                    controller_type = 'admin'
                r['permissions'] = int.from_bytes(d[1], byteorder='little')
                r['controllerType'] = controller_type
        return tmp

    def get_events(self, characteristics, callback_fun, max_events=-1, max_seconds=-1):
        # TODO implementation still missing
        pass

    def identify(self):
        """
        This call can be used to trigger the identification of a paired accessory. A successful call should
        cause the accessory to perform some specific action by which it can be distinguished from the others (blink a
        LED for example).

        It uses the identify characteristic as described on page 152 of the spec.

        :return True, if the identification was run, False otherwise
        """
        if not self.session:
            self.session = BleSession(self.pairing_data, self.adapter)
        cid = -1
        aid = -1
        for a in self.pairing_data['accessories']:
            for s in a['services']:
                for c in s['characteristics']:
                    if CharacteristicsTypes.get_short_uuid(c['type'].upper()) == CharacteristicsTypes.IDENTIFY:
                        aid = a['aid']
                        cid = c['iid']
        self.put_characteristics([(aid, cid, True)])
        # TODO check for errors
        return True

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
            self.session = BleSession(self.pairing_data, self.adapter)

        results = {}
        for aid, cid in characteristics:
            try:
                fc, fc_info = self.session.find_characteristic_by_iid(cid)
                if not fc or not fc_info:
                    results[(aid, cid)] = {
                        'status': HapBleStatusCodes.INVALID_REQUEST,
                        'description': HapBleStatusCodes[HapBleStatusCodes.INVALID_REQUEST]
                    }
                    continue
                response = self.session.request(fc, cid, HapBleOpCodes.CHAR_READ)
            except Exception as e:
                self.session.close()
                self.session = None
                raise e

            value = self._convert_to_python(aid, cid, response[1]) if 1 in response else None

            results[(aid, cid)] = {
                'value': value
            }

        return results

    def _convert_from_python(self, aid, cid, value):
        """
        Convert a python value into a representation usable for the Bluetooth LE transport. The type to be used will be
        queried from the characteristic.

        :param aid: the accessory id
        :param cid: the characteristic id
        :param value: the value to convert (as python value)
        :return: the converted value as bytes
        """
        char_format = None
        characteristic = self._find_characteristic_in_pairing_data(aid, cid)
        if characteristic:
            char_format = characteristic['format']
        logger.debug('value: %s format: %s', value, char_format)

        if char_format == CharacteristicFormats.bool:
            try:
                val = strtobool(str(value))
            except ValueError:
                raise FormatError('"{v}" is no valid "{t}"!'.format(v=value, t=char_format))
            return struct.pack('?', val)

        # no  more boolean input after this line
        if type(value) == bool:
            raise FormatError('"{v}" is no valid "{t}"!'.format(v=value, t=char_format))

        if char_format == CharacteristicFormats.float:
            try:
                return struct.pack('f', float(value))
            except ValueError:
                raise FormatError('"{v}" is no valid "{t}"!'.format(v=value, t=char_format))

        if char_format == CharacteristicFormats.string:
            if type(value) != str:
                raise FormatError('"{v}" is no valid "{t}"!'.format(v=value, t=char_format))
            return value.encode('UTF-8')

        if char_format == CharacteristicFormats.data or char_format == CharacteristicFormats.tlv8:
            return value.hex().encode()

        # from here only integer values of different sizes
        if char_format == CharacteristicFormats.int:
            try:
                if float(value) != int(value):
                    raise FormatError('"{v}" is no valid "{t}"!'.format(v=value, t=char_format))
                value = struct.pack('i', int(value))
            except ValueError:
                raise FormatError('"{v}" is no valid "{t}"!'.format(v=value, t=char_format))
        elif char_format == CharacteristicFormats.uint8:
            try:
                if float(value) != int(value):
                    raise FormatError('"{v}" is no valid "{t}"!'.format(v=value, t=char_format))
                value = struct.pack('B', int(value))
            except ValueError:
                raise FormatError('"{v}" is no valid "{t}"!'.format(v=value, t=char_format))
            except struct.error:
                raise FormatError('"{v}" is no valid "{t}"!'.format(v=value, t=char_format))
        elif char_format == CharacteristicFormats.uint16:
            try:
                if float(value) != int(value):
                    raise FormatError('"{v}" is no valid "{t}"!'.format(v=value, t=char_format))
                value = struct.pack('H', int(value))
            except ValueError:
                raise FormatError('"{v}" is no valid "{t}"!'.format(v=value, t=char_format))
            except struct.error:
                raise FormatError('"{v}" is no valid "{t}"!'.format(v=value, t=char_format))
        elif char_format == CharacteristicFormats.uint32:
            try:
                if float(value) != int(value):
                    raise FormatError('"{v}" is no valid "{t}"!'.format(v=value, t=char_format))
                value = struct.pack('I', int(value))
            except ValueError:
                raise FormatError('"{v}" is no valid "{t}"!'.format(v=value, t=char_format))
            except struct.error:
                raise FormatError('"{v}" is no valid "{t}"!'.format(v=value, t=char_format))
        elif char_format == CharacteristicFormats.uint64:
            try:
                if float(value) != int(value):
                    raise FormatError('"{v}" is no valid "{t}"!'.format(v=value, t=char_format))
                value = struct.pack('Q', int(value))
            except ValueError:
                raise FormatError('"{v}" is no valid "{t}"!'.format(v=value, t=char_format))
            except struct.error:
                raise FormatError('"{v}" is no valid "{t}"!'.format(v=value, t=char_format))
        return value

    def _convert_to_python(self, aid, cid, value):
        """
        Convert a value from the Bluetooth LE transport to python values.

        :param aid: the accessory id
        :param cid: the characteristic id
        :param value: the value as bytes
        :return: the converted value as python value
        """
        char_format = None
        characteristic = self._find_characteristic_in_pairing_data(aid, cid)
        if characteristic:
            char_format = characteristic['format']
        logger.debug('value: %s format: %s', value.hex(), char_format)

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

    def _find_characteristic_in_pairing_data(self, aid, cid):
        """
        Iterate over the accessories in the pairing data. If a characteristic with the correct accessory id and
        characteristic id is found, the characteristic is returned. If no characteristic is found, it returns None.

        :param aid: the accessory id
        :param cid: the characteristic id
        :return: the characteristic or None
        """
        for a in self.pairing_data['accessories']:
            if a['aid'] == int(aid):
                for s in a['services']:
                    for c in s['characteristics']:
                        if c['iid'] == int(cid):
                            return c
        return None

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
            self.session = BleSession(self.pairing_data, self.adapter)

        results = {}

        for aid, cid, value in characteristics:
            # reply with an error if the characteristic does not exist
            if not self._find_characteristic_in_pairing_data(aid, cid):
                results[(aid, cid)] = {
                    'status': HapBleStatusCodes.INVALID_REQUEST,
                    'description': HapBleStatusCodes[HapBleStatusCodes.INVALID_REQUEST]
                }
                continue

            value = TLV.encode_list([(1, self._convert_from_python(aid, cid, value))])
            body = len(value).to_bytes(length=2, byteorder='little') + value

            try:
                fc, fc_info = self.session.find_characteristic_by_iid(cid)
                response = self.session.request(fc, cid, HapBleOpCodes.CHAR_WRITE, body)
                logger.debug('response %s', response)
                # TODO does the response contain useful information here?
            except RequestRejected as e:
                results[(aid, cid)] = {
                    'status': e.status,
                    'description': e.message,
                }
            except Exception as e:
                self.session.close()
                self.session = None
                raise e

        return results

    def add_pairing(self, additional_controller_pairing_identifier, ios_device_ltpk, permissions):
        if not self.session:
            self.session = BleSession(self.pairing_data, self.adapter)
        if permissions == 'User':
            permissions = TLV.kTLVType_Permission_RegularUser
        elif permissions == 'Admin':
            permissions = TLV.kTLVType_Permission_AdminUser
        else:
            print('UNKNOWN')

        request_tlv = TLV.encode_list([
            (TLV.kTLVType_State, TLV.M1),
            (TLV.kTLVType_Method, TLV.AddPairing),
            (TLV.kTLVType_Identifier, additional_controller_pairing_identifier.encode()),
            (TLV.kTLVType_PublicKey, bytes.fromhex(ios_device_ltpk)),
            (TLV.kTLVType_Permissions, permissions)
        ])

        request_tlv = TLV.encode_list([
            (TLV.kTLVHAPParamParamReturnResponse, bytearray(b'\x01')),
            (TLV.kTLVHAPParamValue, request_tlv)
        ])
        body = len(request_tlv).to_bytes(length=2, byteorder='little') + request_tlv

        cid = -1
        for a in self.pairing_data['accessories']:
            for s in a['services']:
                for c in s['characteristics']:
                    if CharacteristicsTypes.get_short_uuid(c['type'].upper()) == CharacteristicsTypes.PAIRING_PAIRINGS:
                        cid = c['iid']
        fc, _ = self.session.find_characteristic_by_iid(cid)
        response = self.session.request(fc, cid, HapBleOpCodes.CHAR_WRITE, body)
        # TODO handle response properly
        print('unhandled response:', response)


class BleSession(object):

    def __init__(self, pairing_data, adapter):
        self.adapter = adapter
        self.pairing_data = pairing_data
        self.c2a_counter = 0
        self.a2c_counter = 0
        self.c2a_key = None
        self.a2c_key = None
        self.device = None
        mac_address = self.pairing_data['AccessoryMAC']

        manager = DeviceManager(self.adapter)

        self.device = manager.make_device(mac_address)
        logger.debug('connecting to device')
        self.device.connect()
        logger.debug('connected to device')

        uuid_map = {}
        for s in self.device.services:
            for c in s.characteristics:
                uuid_map[(s.uuid.upper(), c.uuid.upper())] = c

        self.uuid_map = {}
        self.iid_map = {}
        self.short_map = {}
        for a in pairing_data['accessories']:
            for s in a['services']:
                s_short = None
                if s['type'].endswith(ServicesTypes.baseUUID):
                    s_short = s['type'].split('-', 1)[0].lstrip('0')

                for c in s['characteristics']:
                    char = uuid_map.get((s['type'], c['type']), None)
                    if not char:
                        continue
                    self.iid_map[c['iid']] = (char, c)
                    self.uuid_map[(s['type'], c['type'])] = (char, c)

                    if s_short and c['type'].endswith(CharacteristicsTypes.baseUUID):
                        c_short = c['type'].split('-', 1)[0].lstrip('0')
                        self.short_map[(s_short, c_short)] = (char, c)

                    service_type_short = ServicesTypes.get_short(s['type'])
                    characteristic_type_short = CharacteristicsTypes.get_short(c['type'])
                    self.short_map[service_type_short, characteristic_type_short] = (char, c)

        pair_verify_char, pair_verify_char_info = self.short_map.get(
            (ServicesTypes.PAIRING_SERVICE, CharacteristicsTypes.PAIR_VERIFY),
            (None, None)
        )

        if not pair_verify_char:
            print('verify characteristic not found')
            # TODO Have exception here
            sys.exit(-1)

        write_fun = create_ble_pair_setup_write(pair_verify_char, pair_verify_char_info['iid'])
        self.c2a_key, self.a2c_key = get_session_keys(None, self.pairing_data, write_fun)
        logger.debug('pair_verified, keys: \n\t\tc2a: %s\n\t\ta2c: %s', self.c2a_key.hex(), self.a2c_key.hex())

        self.c2a_counter = 0
        self.a2c_counter = 0

    def __del__(self):
        self.close()

    def close(self):
        logger.debug('closing session')
        self.device.disconnect()

    def find_characteristic_by_iid(self, cid):
        return self.iid_map.get(cid, (None, None))

    def request(self, feature_char, feature_char_id, op, body=None):
        transaction_id = random.randrange(0, 255)

        data = bytearray([0x00, op, transaction_id])
        data.extend(feature_char_id.to_bytes(length=2, byteorder='little'))

        if body:
            logger.debug('body: %s', body)
            data.extend(body)

        logger.debug('data: %s', data)

        cnt_bytes = self.c2a_counter.to_bytes(8, byteorder='little')
        cipher_and_mac = chacha20_aead_encrypt(bytes(), self.c2a_key, cnt_bytes, bytes([0, 0, 0, 0]), data)
        cipher_and_mac[0].extend(cipher_and_mac[1])
        data = cipher_and_mac[0]
        logger.debug('cipher and mac %s', cipher_and_mac[0].hex())

        result = feature_char.write_value(value=data)
        logger.debug('write resulted in: %s', result)

        self.c2a_counter += 1

        data = []
        while not data or len(data) == 0:
            time.sleep(1)
            logger.debug('reading characteristic')
            data = feature_char.read_value()
            if not data and not self.device.is_connected():
                raise AccessoryDisconnectedError('Characteristic read failed')

        resp_data = bytearray([b for b in data])
        logger.debug('read: %s', bytearray(resp_data).hex())

        data = chacha20_aead_decrypt(bytes(), self.a2c_key, self.a2c_counter.to_bytes(8, byteorder='little'),
                                     bytes([0, 0, 0, 0]), resp_data)

        logger.debug('decrypted: %s', bytearray(data).hex())

        if not data:
            return {}

        # parse header and check stuff
        logger.debug('parse sig read response %s', bytes([int(a) for a in data]).hex())

        # handle the header data
        cf = data[0]
        logger.debug('control field %d', cf)
        tid = data[1]
        logger.debug('transaction id %d (expected was %d)', tid, transaction_id)
        status = data[2]
        logger.debug('status code %d (%s)', status, HapBleStatusCodes[status])
        assert cf == 0x02
        assert tid == transaction_id

        if status != HapBleStatusCodes.SUCCESS:
            raise RequestRejected(status, HapBleStatusCodes[status])

        self.a2c_counter += 1

        # get body length
        length = int.from_bytes(data[3:5], byteorder='little')
        logger.debug('expected body length %d (got %d)', length, len(data[5:]))

        # parse tlvs and analyse information
        tlv = TLV.decode_bytes(data[5:])
        logger.debug('received TLV: %s', TLV.to_string(tlv))
        return dict(tlv)


def find_characteristic_by_uuid(device, service_uuid, char_uuid):
    """
    # TODO document me

    :param device:
    :param service_uuid:
    :param char_uuid:
    :return:
    """
    service_found = None
    logger.debug('services: %s', device.services)
    for possible_service in device.services:
        if ServicesTypes.get_short(service_uuid.upper()) == ServicesTypes.get_short(possible_service.uuid.upper()):
            service_found = possible_service
            break
    logger.debug('searched service: %s', service_found)

    if not service_found:
        logging.error('searched service not found.')
        return None, None

    result_char = None
    result_char_id = None
    for characteristic in service_found.characteristics:
        logger.debug('char: %s %s', characteristic.uuid, CharacteristicsTypes.get_short(characteristic.uuid.upper()))
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

    logger.debug('searched char: %s %s', result_char, result_char_id)
    return result_char, result_char_id


def create_ble_pair_setup_write(characteristic, characteristic_id):
    def write(request, expected):
        # TODO document me
        logger.debug('entering write function %s', TLV.to_string(TLV.decode_bytes(request)))
        request_tlv = TLV.encode_list([
            (TLV.kTLVHAPParamParamReturnResponse, bytearray(b'\x01')),
            (TLV.kTLVHAPParamValue, request)
        ])
        transaction_id = random.randrange(0, 255)
        data = bytearray([0x00, HapBleOpCodes.CHAR_WRITE, transaction_id])
        data.extend(characteristic_id.to_bytes(length=2, byteorder='little'))
        data.extend(len(request_tlv).to_bytes(length=2, byteorder='little'))
        data.extend(request_tlv)
        logger.debug('sent %s', bytes(data).hex())
        characteristic.write_value(value=data)
        data = []
        while len(data) == 0:
            time.sleep(1)
            logger.debug('reading characteristic')
            data = characteristic.read_value()
        resp_data = [b for b in data]

        expected_length = int.from_bytes(bytes(resp_data[3:5]), byteorder='little')
        logger.debug(
            'control field: {c:x}, tid: {t:x}, status: {s:x}, length: {length}'.format(c=resp_data[0], t=resp_data[1],
                                                                                       s=resp_data[2],
                                                                                       length=expected_length))
        while len(resp_data[3:]) < expected_length:
            time.sleep(1)
            logger.debug('reading characteristic')
            data = characteristic.read_value()
            resp_data.extend([b for b in data])
            logger.debug('data %s of %s', len(resp_data[3:]), expected_length)

        logger.debug('received %s', bytes(resp_data).hex())
        logger.debug('decode %s', bytes(resp_data[5:]).hex())
        resp_tlv = TLV.decode_bytes(bytes([int(a) for a in resp_data[5:]]), expected=[TLV.kTLVHAPParamValue])
        result = TLV.decode_bytes(resp_tlv[0][1], expected)
        logger.debug('leaving write function %s', TLV.to_string(result))
        return result

    return write


class ResolvingManager(DeviceManager):
    """
    DeviceManager implementation that stops running after a given device was discovered.
    """

    def __init__(self, adapter_name, mac):
        self.mac = mac
        DeviceManager.__init__(self, adapter_name=adapter_name)

    def device_discovered(self, device):
        logger.debug('discovered %s', device.mac_address.upper())
        if device.mac_address.upper() == self.mac.upper():
            self.stop()
            # the searched device was found, so we can stop discovery here
            self.stop_discovery()


def read_characteristics(device):
    # TODO document me
    # FIXME: This only works on non secure sessions
    logger.debug('resolved %d services', len(device.services))

    a_data = {
        'aid': 1,
        'services': []
    }

    resolved_data = {
        'data': [a_data],
    }

    for service in device.services:
        logger.debug('found service with UUID %s (%s)', service.uuid,
                     ServicesTypes.get_short(service.uuid.upper()))

        s_data = {
            'characteristics': [
            ],
            'iid': None
        }

        for characteristic in service.characteristics:
            logger.debug('\tfound characteristic with UUID %s (%s)', characteristic.uuid,
                         CharacteristicsTypes.get_short(characteristic.uuid.upper()))

            if characteristic.uuid.upper() == CharacteristicsTypes.SERVICE_INSTANCE_ID:
                sid = int.from_bytes(characteristic.read_value(), byteorder='little')
                logger.debug('\t\tread service id %d', sid)
                s_data['iid'] = sid
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
                        logger.debug('\t\tread characteristic id %d', iid)
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
                            s_data['type'] = d[k].upper()
                        elif k == 'sid':
                            s_data['iid'] = d[k]
                        else:
                            c_data[k] = d[k]

                if c_data['iid']:
                    s_data['characteristics'].append(c_data)

        if s_data['iid']:
            a_data['services'].append(s_data)

    logger.debug('data: %s', resolved_data)

    return resolved_data


def parse_sig_read_response(data, expected_tid):
    # TODO document me
    # parse header and check stuff
    logger.debug('parse sig read response %s', bytes([int(a) for a in data]).hex())

    # handle the header data
    cf = data[0]
    logger.debug('control field %d', cf)
    tid = data[1]
    logger.debug('transaction id %d (expected was %d)', tid, expected_tid)
    status = data[2]
    logger.debug('status code %d (%s)', status, HapBleStatusCodes[status])
    assert cf == 0x02
    assert tid == expected_tid
    assert status == HapBleStatusCodes.SUCCESS

    # get body length
    length = int.from_bytes(data[3:5], byteorder='little')
    logger.debug('expected body length %d (got %d)', length, len(data[5:]))

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
            logger.debug('range: %s', t[1].hex())
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
              'type': chr_type.upper(), 'sid': svc_id, 'service_type': svc_type}
    logger.debug('result: %s', str(result))

    return result
