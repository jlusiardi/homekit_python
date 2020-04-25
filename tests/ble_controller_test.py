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

import binascii
import unittest
from unittest import mock
import uuid
import logging
import tlv8
import dbus

from homekit.crypto.chacha20poly1305 import chacha20_aead_decrypt, chacha20_aead_encrypt
from homekit import Controller
from homekit.model import Accessory
from homekit.model.characteristics import CharacteristicsTypes
from homekit.model.services import ServicesTypes, AbstractService, LightBulbService
from homekit.model.characteristics import AbstractCharacteristic
from homekit.protocol import States, Methods, TlvTypes
from homekit import accessoryserver
from homekit.model import mixin as model_mixin
from homekit import exceptions

from homekit.tools import BLE_TRANSPORT_SUPPORTED

if BLE_TRANSPORT_SUPPORTED:
    from homekit.controller.ble_impl import CharacteristicInstanceID, AdditionalParameterTypes
    from homekit.protocol.opcodes import HapBleOpCodes
    from homekit.model.characteristics.characteristic_formats import BleCharacteristicFormats
    from homekit.controller.ble_impl.manufacturer_data import parse_manufacturer_specific
    from homekit.model.status_flags import BleStatusFlags


class DeviceManager:
    """
    This is a fake version of gatt.DeviceManager
    """

    def __init__(self):
        self._devices = {}

    def make_device(self, mac_address):
        return self._devices[mac_address]

    def start_discovery(self, callback=None):
        pass

    def set_timeout(self, timeout):
        pass

    def run(self):
        pass

    def devices(self):
        return self._devices.values()


class Device:
    """
    This is a fake version of a gatt.Device
    """

    connected = False

    def __init__(self, accessory: Accessory):
        self.accessory = accessory
        self.name = 'Test'  # FIXME get from accessory
        self.mac_address = '00:00:00:00:00'

        # Data needed by pair-setup and pair-verify
        self.is_paired = False
        self.unsuccessful_tries = 0
        self.setup_code = '111-11-111'
        self.accessory_ltpk = None  # b'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
        self.accessory_ltsk = None  # b'YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY'
        self.accessory_pairing_id_bytes = b'12:00:00:00:00:00'

        self.session_id = 'XXX'
        self.sessions = {'XXX': {}}

        self.peers = {}

        self.services = []
        for service in accessory.services:
            self.services.append(Service(self, service))

        self.services.append(PairingServiceHandler(self))

    def set_accessory_keys(self, ltpk, ltsk):
        self.accessory_ltpk = ltpk
        self.accessory_ltsk = ltsk

    def add_peer(self, pairing_id: bytes, ltpk: bytes, admin: bool):
        # admin = len(self.peers) == 0
        self.peers[pairing_id.decode()] = {
            'key': binascii.hexlify(ltpk).decode(),
            'admin': admin,
        }

    def get_peer_key(self, pairing_id: bytes):
        if pairing_id.decode() not in self.peers:
            return
        return bytes.fromhex(self.peers[pairing_id.decode()]['key'])

    def get_homekit_discovery_data(self):
        data = {
            'acid': 9,
            'category': 'Thermostat',
            'cn': 2,
            'cv': 2,
            'device_id': '99:99:99:99:99:99',
            'flags': 'paired',
            'gsn': 3985,
            'manufacturer': 'apple',
            'sf': 0,
            'type': 'HomeKit'
        }

        if len(self.peers) > 0:
            data['flags'] = 'paired'
            data['sf'] = 0
        else:
            data['flags'] = 'unpaired'
            data['sf'] = 1

        return data

    @property
    def homekit_discovery_data(self):
        return self.get_homekit_discovery_data()

    def connect(self):
        self.connected = True

    def disconnect(self):
        self.connected = False

    def is_connected(self):
        return self.connected


class Service:
    """
    This is a fake version of gatt.Service
    """

    def __init__(self, device, service):
        self.device = device
        self.service = service

        self.characteristics = []
        for char in service.characteristics:
            self.characteristics.append(Characteristic(self, char))

        self.characteristics.append(ServiceInstanceId(self))

    @property
    def uuid(self):
        return self.service.type.upper()


class ServiceEntry(AbstractService):
    """
    This is just to allow a service to be instanced directly for testing
    purposes.
    """


class PairingServiceHandler(Service):
    """
    This is a fake version of gatt.Service

    This special cases the pairing endpoints, which speak a different protocol
    to the other endpoints.
    """

    def __init__(self, device):
        service = ServiceEntry(
            ServicesTypes.get_uuid('public.hap.service.pairing'),
            model_mixin.get_id(),
        )

        super().__init__(device, service)

        self.characteristics.append(PairingSetupCharacteristicHandler(self))
        self.characteristics.append(PairingVerifyCharacteristicHandler(self))
        self.characteristics.append(PairingPairingsCharacteristicHandler(self))


class Characteristic:
    """
    This is a fake version of gatt.Characteristic

    When `write_value` is called, it parses the value into a command to be
    performed against the underlying homekit.model and performs it. It the
    queues up a response that is returned the next time `read_value` is called.

    If a secure session has been established encryption will be handled automatically.
    """

    def __init__(self, service, char):
        self.service = service
        self.char = char

        self.descriptors = []

        self.descriptors.append(Descriptor(
            self,
            CharacteristicInstanceID,
            self.char.iid.to_bytes(length=8, byteorder='little'),
        ))

        self.values = []

    @property
    def uuid(self):
        return self.char.type.upper()

    def decrypt_value(self, value):
        device = self.service.device
        session = device.sessions[device.session_id]

        if 'controller_to_accessory_key' in session:
            c2a_key = session['controller_to_accessory_key']
            cnt_bytes = session['controller_to_accessory_count'].to_bytes(8, byteorder='little')
            value = chacha20_aead_decrypt(b'', c2a_key, cnt_bytes, bytes([0, 0, 0, 0]), value)
            session['controller_to_accessory_count'] += 1

        return value

    def encrypt_value(self, value):
        device = self.service.device
        session = device.sessions[device.session_id]
        if 'accessory_to_controller_key' in session:
            a2c_key = session['accessory_to_controller_key']
            cnt_bytes = session['accessory_to_controller_count'].to_bytes(8, byteorder='little')
            ciper_and_mac = chacha20_aead_encrypt(b'', a2c_key, cnt_bytes, bytes([0, 0, 0, 0]), value)
            session['accessory_to_controller_count'] += 1
            value = ciper_and_mac[0] + ciper_and_mac[1]
        return value

    def do_char_write(self, tid, value):
        self.char.set_value_from_ble(value)

        response = bytearray([0x02, tid, 0x00])
        self.queue_read_response(self.encrypt_value(bytes(response)))

    def process_value(self, value):
        assert value[0] == 0
        opcode = value[1]
        tid = value[2]
        payload = value[7:]

        if opcode == HapBleOpCodes.CHAR_WRITE:
            new_value = {entry.type_id: entry.data for entry in tlv8.decode(payload)}
            self.do_char_write(tid, new_value[1])

        elif opcode == HapBleOpCodes.CHAR_READ:
            value = self.char.get_value_for_ble()
            value = tlv8.encode([tlv8.Entry(AdditionalParameterTypes.Value, value)])

            response = bytearray([0x02, tid, 0x00])
            tlv = len(value).to_bytes(2, byteorder='little') + value
            response.extend(tlv)
            self.queue_read_response(self.encrypt_value(bytes(response)))

        elif opcode == HapBleOpCodes.CHAR_SIG_READ:
            response = bytearray([0x02, tid, 0x00])

            service_type = list(uuid.UUID(self.service.service.type).bytes)
            service_type.reverse()
            service_type = bytes(bytearray(service_type))

            char_type = list(uuid.UUID(self.char.type).bytes)
            char_type.reverse()
            char_type = bytes(bytearray(char_type))

            fmt = BleCharacteristicFormats.get_reverse(self.char.format, b'\x00').to_bytes(length=1, byteorder='little')
            unit = b'\x00\x00'
            gatt_fmt = fmt + unit

            data = [
                tlv8.Entry(AdditionalParameterTypes.HAPCharacteristicPropertiesDescriptor, b'\x00'),
                tlv8.Entry(AdditionalParameterTypes.GATTPresentationFormatDescriptor, gatt_fmt),
                tlv8.Entry(AdditionalParameterTypes.CharacteristicType, char_type),
                tlv8.Entry(AdditionalParameterTypes.ServiceInstanceId,
                           self.service.service.iid.to_bytes(length=8, byteorder='little')),
                tlv8.Entry(AdditionalParameterTypes.ServiceType, service_type),
            ]

            tlv = tlv8.encode(data)
            response.extend(len(tlv).to_bytes(2, byteorder='little') + tlv)
            self.queue_read_response(self.encrypt_value(bytes(response)))
        else:
            raise RuntimeError('Fake does not implement opcode %s' % opcode)

    def write_value(self, value):
        return self.process_value(self.decrypt_value(value))

    def queue_read_response(self, value):
        if not self.service.device.connected:
            return
        self.values.append(value)

    def read_value(self):
        # real world objects return a dbus.Array object here, this array contains dbus.Byte values.
        # dbus.Array([dbus.Byte(2), ..., dbus.Byte(1)], signature=dbus.Signature('y'))
        if not self.values:
            return dbus.Array(b'')

        val = [dbus.Byte(x) for x in self.values.pop(0)]
        ar = dbus.Array(val)
        return ar


class ServiceInstanceId(Characteristic):
    """
    This is a fake gatt.Characteristic.

    It is a special case for returning this services iid via the
    SERVICES_INSTANCE_ID endpoint.
    """

    def __init__(self, service):
        self.service = service

    @property
    def uuid(self):
        return CharacteristicsTypes.SERVICE_INSTANCE_ID

    def read_value(self):
        return self.service.service.iid.to_bytes(length=2, byteorder='little')


class AccessoryRequestHandler(accessoryserver.AccessoryRequestHandler):
    """
    This extends the HTTP AccessoryRequestHandler object for use from a BLE
    Fake device.

    FIXME: Both this and the actual accessoryserver implementation could
    probably use some refactoring to make this approach a little cleaner.
    """

    def __init__(self, char):
        self.server = self
        self.data = char.service.device
        self.session_id = self.data.session_id
        self.sessions = self.data.sessions

    def log_request(self, *args):
        pass

    def log_message(self, message, *args):
        logging.debug('%s', message % args)

    def log_error(self, message, *args):
        logging.debug('%s', message % args)

    def send_error(self, *args):
        assert False, 'sent error'

    def publish_device(self, *args):
        pass

    def send_error_reply(self, state, error):
        d_res = [
            tlv8.Entry(TlvTypes.State, state),
            tlv8.Entry(TlvTypes.Error, error)
        ]
        self._send_response_tlv(d_res)

    def _send_response_tlv(self, d_res, close=False, status=None):
        result_bytes = tlv8.encode(d_res)

        outer = tlv8.encode([
            tlv8.Entry(AdditionalParameterTypes.Value, result_bytes),
        ])
        self.value += b'\x00' + len(outer).to_bytes(length=2, byteorder='little') + outer

    def process_setup(self, tid, value):
        self.value = b'\x00' + tid.to_bytes(length=1, byteorder='little')
        self.body = value
        self._post_pair_setup()
        return self.value

    def process_verify(self, tid, value):
        self.value = b'\x00' + tid.to_bytes(length=1, byteorder='little')
        self.body = value
        self._post_pair_verify()
        return self.value


class CharacteristicEntry(AbstractCharacteristic):
    """
    We cant instance an AbstractCharacteristic directly. This is just so we can
    create test characteristics quickly and without needed loads of custom
    subclasses.
    """


class PairingSetupCharacteristicHandler(Characteristic):
    """
    This is a fake gatt.Characteristic.

    Its to handle the special case of pairing a new device.
    """

    def __init__(self, service):
        characteristic = CharacteristicEntry(
            model_mixin.get_id(),
            'public.hap.characteristic.pairing.pair-setup',
            'data',
        )

        super().__init__(service, characteristic)

        self.rh = AccessoryRequestHandler(self)

        self.values = []

    def write_value(self, value):
        assert value[0] == 0
        opcode = value[1]

        if opcode == 2:
            outer = {entry.type_id: entry.data for entry in tlv8.decode(value[7:])}
            assert outer[AdditionalParameterTypes.ParamReturnResponse] == b'\x01'

            value = self.rh.process_setup(value[2], outer[AdditionalParameterTypes.Value])
            self.values.append(value)
        else:
            super().write_value(value)


class PairingVerifyCharacteristicHandler(Characteristic):
    """
    This is a fake gatt.Characteristic.

    Its to handle the special case of established a new secure session with a device.
    """

    def __init__(self, service):
        characteristic = CharacteristicEntry(
            model_mixin.get_id(),
            'public.hap.characteristic.pairing.pair-verify',
            'data',
        )

        super().__init__(service, characteristic)

        self.rh = AccessoryRequestHandler(self)

        self.values = []

    def write_value(self, value):
        assert value[0] == 0
        opcode = value[1]

        if opcode == 2:
            outer = {entry.type_id: entry.data for entry in tlv8.decode(value[7:])}
            assert outer[AdditionalParameterTypes.ParamReturnResponse] == b'\x01'

            value = self.rh.process_verify(value[2], outer[AdditionalParameterTypes.Value])
            self.values.append(value)
        else:
            super().write_value(value)


class PairingPairingsCharacteristicHandler(Characteristic):
    """
    This is a fake gatt.Characteristic.

    Its to handle the special case of managing pairings on a fake accessory.
    """

    def __init__(self, service):
        characteristic = CharacteristicEntry(
            model_mixin.get_id(),
            'public.hap.characteristic.pairing.pairings',
            'data',
        )

        super().__init__(service, characteristic)

        self.values = []

    def do_char_write(self, tid, value):
        """The value is actually a TLV with a command to perform"""

        request = {entry.type_id: entry.data for entry in tlv8.decode(value, {
            TlvTypes.State: tlv8.DataType.INTEGER,
            TlvTypes.Method: tlv8.DataType.INTEGER,
            TlvTypes.Identifier: tlv8.DataType.BYTES,
        })}
        logging.debug('%s', request)

        assert request[TlvTypes.State] == States.M1

        if request[TlvTypes.Method] == Methods.RemovePairing:
            ident = request[TlvTypes.Identifier].decode()
            self.service.device.peers.pop(ident, None)

            # If ident == this session then disconnect it
            # self.service.device.disconnect()

        response = bytearray([0x02, tid, 0x00])

        inner = tlv8.encode([
            tlv8.Entry(TlvTypes.State, States.M2),
        ])

        outer = tlv8.encode([tlv8.Entry(AdditionalParameterTypes.Value, inner)])
        response.extend(len(outer).to_bytes(length=2, byteorder='little'))
        response.extend(outer)

        self.queue_read_response(self.encrypt_value(bytes(response)))


class Descriptor:
    """
    A fake gatt.Descriptor

    This is just for mapping values to UUID's in a fake characteristic (such as
    a characteristics iid).
    """

    def __init__(self, characteristic, uuid, value):
        self.characteristic = characteristic
        self.uuid = uuid
        self.value = value

    def read_value(self):
        return self.value


@unittest.skipIf(not BLE_TRANSPORT_SUPPORTED, 'BLE no supported')
class TestBLEController(unittest.TestCase):
    def test_discovery(self):
        model_mixin.id_counter = 0

        c = Controller()

        a = Accessory(
            'test-dev-123',
            'TestCo',
            'Test Dev Pro',
            '00000',
            1
        )
        a.add_service(LightBulbService())

        manager = DeviceManager()
        manager._devices['00:00:00:00:00'] = Device(a)

        with mock.patch('homekit.controller.controller.DiscoveryDeviceManager') as m:
            m.return_value = manager

            self.assertEqual(c.discover_ble(0), [{
                'acid': 9,
                'category': 'Thermostat',
                'cn': 2,
                'cv': 2,
                'device_id': '99:99:99:99:99:99',
                'flags': 'unpaired',
                'gsn': 3985,
                'mac': '00:00:00:00:00',
                'name': 'Test',
                'sf': 1,
            }])

    def test_unpaired_identify(self):
        model_mixin.id_counter = 0

        c = Controller()

        a = Accessory(
            'test-dev-123',
            'TestCo',
            'Test Dev Pro',
            '00000',
            1
        )
        a.add_service(LightBulbService())

        manager = DeviceManager()
        manager._devices['00:00:00:00:00'] = Device(a)

        with mock.patch('homekit.controller.ble_impl.device.DeviceManager') as m:
            m.return_value = manager
            self.assertIsNone(a.services[0].characteristics[0].value)
            self.assertTrue(c.identify_ble('00:00:00:00:00'))
            self.assertTrue(a.services[0].characteristics[0].value)

    def test_unpaired_identify_already_paired(self):
        model_mixin.id_counter = 0

        c = Controller()

        a = Accessory(
            'test-dev-123',
            'TestCo',
            'Test Dev Pro',
            '00000',
            1
        )
        a.add_service(LightBulbService())

        manager = DeviceManager()
        manager._devices['00:00:00:00:00'] = Device(a)

        with mock.patch('homekit.controller.ble_impl.device.DeviceManager') as m:
            m.return_value = manager
            c.perform_pairing_ble('test-pairing', '00:00:00:00:00', '111-11-111')
            self.assertIsNone(a.services[0].characteristics[0].value)
            self.assertRaises(exceptions.AlreadyPairedError, c.identify_ble, '00:00:00:00:00')

    def test_pair_success(self):
        model_mixin.id_counter = 0
        c = Controller()

        a = Accessory(
            'test-dev-123',
            'TestCo',
            'Test Dev Pro',
            '00000',
            1
        )
        a.add_service(LightBulbService())

        manager = DeviceManager()
        manager._devices['00:00:00:00:00'] = Device(a)

        with mock.patch('homekit.controller.ble_impl.device.DeviceManager') as m:
            m.return_value = manager
            c.perform_pairing_ble('test-pairing', '00:00:00:00:00', '111-11-111')

        self.assertEqual(c.pairings['test-pairing'].pairing_data['Connection'], 'BLE')

    def test_pair_malformed_pin(self):
        model_mixin.id_counter = 0
        c = Controller()

        a = Accessory(
            'test-dev-123',
            'TestCo',
            'Test Dev Pro',
            '00000',
            1
        )
        a.add_service(LightBulbService())

        manager = DeviceManager()
        manager._devices['00:00:00:00:00'] = Device(a)

        with mock.patch('homekit.controller.ble_impl.device.DeviceManager') as m:
            m.return_value = manager
            c.perform_pairing_ble('test-pairing', '00:00:00:00:00', '111-11-111')
            self.assertRaises(exceptions.MalformedPinError, c.perform_pairing_ble, 'alias2',
                              '12:34:56:00:01:0B', '01022021')

    def test_pair_unpair(self):
        model_mixin.id_counter = 0
        c = Controller()

        a = Accessory(
            'test-dev-123',
            'TestCo',
            'Test Dev Pro',
            '00000',
            1
        )
        a.add_service(LightBulbService())

        manager = DeviceManager()
        device = manager._devices['00:00:00:00:00'] = Device(a)

        with mock.patch('homekit.controller.ble_impl.DeviceManager') as m1:
            with mock.patch('homekit.controller.ble_impl.device.DeviceManager') as m2:
                m1.return_value = manager
                m2.return_value = manager
                c.perform_pairing_ble('test-pairing', '00:00:00:00:00', '111-11-111')
                c.pairings['test-pairing'].list_accessories_and_characteristics()
                self.assertEqual(len(device.peers), 1)

                c.remove_pairing('test-pairing')

                self.assertEqual(len(device.peers), 0)
                self.assertNotIn('test-pairing', c.pairings)

    def test_list_accessories_and_characteristics(self):
        model_mixin.id_counter = 0

        c = Controller()

        a = Accessory(
            'test-dev-123',
            'TestCo',
            'Test Dev Pro',
            '00000',
            1
        )
        a.add_service(LightBulbService())

        manager = DeviceManager()
        manager._devices['00:00:00:00:00'] = Device(a)

        with mock.patch('homekit.controller.ble_impl.device.DeviceManager') as m:
            with mock.patch('homekit.controller.ble_impl.DeviceManager') as m2:
                m.return_value = manager
                m2.return_value = manager
                c.perform_pairing_ble('test-pairing', '00:00:00:00:00', '111-11-111')
                accessories = c.pairings['test-pairing'].list_accessories_and_characteristics()

        self.assertEqual(accessories, [
            {
                "aid": 1,
                "services": [
                    {
                        "characteristics": [
                            {
                                "iid": 3,
                                "type": "00000014-0000-1000-8000-0026BB765291",
                                "perms": [],
                                "description": "",
                                "format": "bool",
                                "unit": "unknown",
                                "range": None,
                                "step": None
                            },
                            {
                                "iid": 4,
                                "type": "00000020-0000-1000-8000-0026BB765291",
                                "perms": [],
                                "description": "",
                                "format": "string",
                                "unit": "unknown",
                                "range": None,
                                "step": None
                            },
                            {
                                "iid": 5,
                                "type": "00000021-0000-1000-8000-0026BB765291",
                                "perms": [],
                                "description": "",
                                "format": "string",
                                "unit": "unknown",
                                "range": None,
                                "step": None
                            },
                            {
                                "iid": 6,
                                "type": "00000023-0000-1000-8000-0026BB765291",
                                "perms": [],
                                "description": "",
                                "format": "string",
                                "unit": "unknown",
                                "range": None,
                                "step": None
                            },
                            {
                                "iid": 7,
                                "type": "00000030-0000-1000-8000-0026BB765291",
                                "perms": [],
                                "description": "",
                                "format": "string",
                                "unit": "unknown",
                                "range": None,
                                "step": None
                            },
                            {
                                "iid": 8,
                                "type": "00000052-0000-1000-8000-0026BB765291",
                                "perms": [],
                                "description": "",
                                "format": "string",
                                "unit": "unknown",
                                "range": None,
                                "step": None
                            }
                        ],
                        "iid": 2,
                        "type": "0000003E-0000-1000-8000-0026BB765291"
                    },
                    {
                        "characteristics": [
                            {
                                "iid": 10,
                                "type": "00000025-0000-1000-8000-0026BB765291",
                                "perms": [],
                                "description": "",
                                "format": "bool",
                                "unit": "unknown",
                                "range": None,
                                "step": None
                            }
                        ],
                        "iid": 9,
                        "type": "00000043-0000-1000-8000-0026BB765291"
                    },
                    {
                        "characteristics": [
                            {
                                "iid": 12,
                                "type": "0000004C-0000-1000-8000-0026BB765291",
                                "perms": [],
                                "description": "",
                                "format": "data",
                                "unit": "unknown",
                                "range": None,
                                "step": None
                            },
                            {
                                "iid": 13,
                                "type": "0000004E-0000-1000-8000-0026BB765291",
                                "perms": [],
                                "description": "",
                                "format": "data",
                                "unit": "unknown",
                                "range": None,
                                "step": None
                            },
                            {
                                "description": "",
                                "format": "data",
                                "iid": 14,
                                "perms": [],
                                "range": None,
                                "step": None,
                                "type": "00000050-0000-1000-8000-0026BB765291",
                                "unit": "unknown"}
                        ],
                        "iid": 11,
                        "type": "00000055-0000-1000-8000-0026BB765291"
                    }
                ]
            }
        ])

    def test_get_characteristic(self):
        model_mixin.id_counter = 0
        c = Controller()

        a = Accessory(
            'test-dev-123',
            'TestCo',
            'Test Dev Pro',
            '00000',
            1
        )
        a.add_service(LightBulbService())

        manager = DeviceManager()
        manager._devices['00:00:00:00:00'] = Device(a)

        with mock.patch('homekit.controller.ble_impl.device.DeviceManager') as m1:
            with mock.patch('homekit.controller.ble_impl.DeviceManager') as m2:
                m1.return_value = manager
                m2.return_value = manager
                c.perform_pairing_ble('test-pairing', '00:00:00:00:00', '111-11-111')
                c.pairings['test-pairing'].list_accessories_and_characteristics()
                result = c.pairings['test-pairing'].get_characteristics([
                    (1, 4),
                ])

        self.assertEqual(result, {
            (1, 4): {
                "value": "TestCo",
            }
        })

    def test_get_characteristic_invalid_iid(self):
        model_mixin.id_counter = 0
        c = Controller()

        a = Accessory(
            'test-dev-123',
            'TestCo',
            'Test Dev Pro',
            '00000',
            1
        )
        a.add_service(LightBulbService())

        manager = DeviceManager()
        manager._devices['00:00:00:00:00'] = Device(a)

        with mock.patch('homekit.controller.ble_impl.device.DeviceManager') as m1:
            with mock.patch('homekit.controller.ble_impl.DeviceManager') as m2:
                m1.return_value = manager
                m2.return_value = manager
                c.perform_pairing_ble('test-pairing', '00:00:00:00:00', '111-11-111')
                c.pairings['test-pairing'].list_accessories_and_characteristics()
                result = c.pairings['test-pairing'].get_characteristics([
                    (2, 1),
                ])

        self.assertEqual(result, {
            (2, 1): {
                "status": 6,
                "description": "Accessory was not able to perform the requested operation",
            }
        })

    def test_get_characteristic_disconnected_read(self):
        model_mixin.id_counter = 0
        c = Controller()

        a = Accessory(
            'test-dev-123',
            'TestCo',
            'Test Dev Pro',
            '00000',
            1
        )
        a.add_service(LightBulbService())

        manager = DeviceManager()
        d = manager._devices['00:00:00:00:00'] = Device(a)

        with mock.patch('homekit.controller.ble_impl.device.DeviceManager') as m1:
            with mock.patch('homekit.controller.ble_impl.DeviceManager') as m2:
                m1.return_value = manager
                m2.return_value = manager
                c.perform_pairing_ble('test-pairing', '00:00:00:00:00', '111-11-111')
                c.pairings['test-pairing'].list_accessories_and_characteristics()

                # Establishes a secure session
                c.pairings['test-pairing'].get_characteristics([(1, 4)])

                # Disconnect from virtual bluetooth device - BleSession doesn't know yet
                d.disconnect()

                # Further reads should throw an error
                self.assertRaises(
                    exceptions.AccessoryDisconnectedError,
                    c.pairings['test-pairing'].get_characteristics,
                    [(1, 4)],
                )

    def test_put_characteristic(self):
        model_mixin.id_counter = 0
        c = Controller()

        a = Accessory(
            'test-dev-123',
            'TestCo',
            'Test Dev Pro',
            '00000',
            1
        )
        a.add_service(LightBulbService())

        manager = DeviceManager()
        manager._devices['00:00:00:00:00'] = Device(a)

        with mock.patch('homekit.controller.ble_impl.device.DeviceManager') as m1:
            with mock.patch('homekit.controller.ble_impl.DeviceManager') as m2:
                m1.return_value = manager
                m2.return_value = manager
                c.perform_pairing_ble('test-pairing', '00:00:00:00:00', '111-11-111')
                c.pairings['test-pairing'].list_accessories_and_characteristics()

                result = c.pairings['test-pairing'].put_characteristics([
                    (1, 10, True),
                ])
                self.assertEqual(result, {})
                self.assertTrue(a.services[1].characteristics[0].get_value())

                result = c.pairings['test-pairing'].put_characteristics([
                    (1, 10, False),
                ])
                self.assertEqual(result, {})
                self.assertFalse(a.services[1].characteristics[0].get_value())

    def test_identify(self):
        model_mixin.id_counter = 0
        c = Controller()

        a = Accessory(
            'test-dev-123',
            'TestCo',
            'Test Dev Pro',
            '00000',
            1
        )
        a.add_service(LightBulbService())

        manager = DeviceManager()
        manager._devices['00:00:00:00:00'] = Device(a)

        with mock.patch('homekit.controller.ble_impl.device.DeviceManager') as m1:
            with mock.patch('homekit.controller.ble_impl.DeviceManager') as m2:
                m1.return_value = manager
                m2.return_value = manager
                c.perform_pairing_ble('test-pairing', '00:00:00:00:00', '111-11-111')
                c.pairings['test-pairing'].list_accessories_and_characteristics()

                self.assertIsNone(a.services[0].characteristics[0].value)
                c.pairings['test-pairing'].identify()
                self.assertTrue(a.services[0].characteristics[0].value)


@unittest.skipIf(not BLE_TRANSPORT_SUPPORTED, 'BLE no supported')
class TestMfrData(unittest.TestCase):
    def test_1(self):
        value = b'\x06\xcd\x00\x99\x99\x99\x99\x99\x99\t\x00\x91\x0f\x02\x02'
        self.assertEqual(parse_manufacturer_specific(value), {
            'acid': 9,
            'category': 'Thermostat',
            'cn': 2,
            'cv': 2,
            'device_id': '99:99:99:99:99:99',
            'gsn': 3985,
            'manufacturer': 'apple',
            'sf': 0,
            'flags': BleStatusFlags[0],
            'type': 'HomeKit'
        })

    def test_2(self):
        value = b'\x061\x00JM\x00\x00\x00\x00\n\x00\x0b\x00\x02\x02RfY\xf8'
        self.assertEqual(parse_manufacturer_specific(value), {
            'acid': 10,
            'category': 'Sensor',
            'cn': 2,
            'cv': 2,
            'device_id': '4A:4D:00:00:00:00',
            'gsn': 11,
            'manufacturer': 'apple',
            'sf': 0,
            'flags': BleStatusFlags[0],
            'type': 'HomeKit'
        })

    def test_3(self):
        value = b'\x061\x01{\x21\x21\x49\x23<\x07\x00B\x00\x02\x02\xb6f\xe1\x1d'
        self.assertEqual(parse_manufacturer_specific(value), {
            'acid': 7,
            'category': 'Outlet',
            'cn': 2,
            'cv': 2,
            'device_id': '7B:21:21:49:23:3C',
            'gsn': 66,
            'manufacturer': 'apple',
            'sf': 1,
            'flags': BleStatusFlags[1],
            'type': 'HomeKit'
        })
