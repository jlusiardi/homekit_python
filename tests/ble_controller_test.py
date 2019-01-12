import binascii
import hashlib
import unittest
from unittest import mock

import gmpy2
import hkdf
import py25519

from homekit.crypto.chacha20poly1305 import chacha20_aead_decrypt, chacha20_aead_encrypt
from homekit import Controller
from homekit.model import Accessory
from homekit.model.characteristics import CharacteristicsTypes
from homekit.model.services import ServicesTypes, AbstractService, LightBulbService
from homekit.model.characteristics import AbstractCharacteristic
from homekit.controller.ble_implementation import CharacteristicInstanceID
from homekit.protocol import TLV
from homekit.crypto.srp import SrpServer
from homekit import accessoryserver
from homekit.protocol.opcodes import HapBleOpCodes
from homekit.model.characteristics.characteristic_formats import BleCharacteristicFormats
from homekit.model import mixin as model_mixin

class DeviceManager:

    """
    This is a fake version of gatt.DeviceManager
    """

    def __init__(self):
        self.devices = {}

    def make_device(self, mac_address):
        return self.devices[mac_address]


class Device:

    """
    This is a fake version of a gatt.Device
    """

    connected = False

    def __init__(self, accessory: Accessory):
        self.accessory = accessory

        # Data needed by pair-setup and pair-verify
        self.is_paired = False
        self.unsuccessful_tries = 0
        self.setup_code = '111-11-111'
        self.accessory_ltpk = b'XXX'
        self.accessory_ltsk = b'XXX'
        self.accessory_pairing_id_bytes = b'12:00:00:00:00:00'

        self.session_id = 'XXX'
        self.sessions = {'XXX': {}}

        self.peers = {}

        self.services = []
        for service in accessory.services:
            self.services.append(Service(self, service))

        self.services.append(PairingServiceHandler(self))

    def add_peer(self, pairing_id: bytes, ltpk: bytes):
        admin = len(self.peers) == 0
        self.peers[pairing_id.decode()] = {
            'key': binascii.hexlify(ltpk).decode(),
            'admin': admin,
        }

    def get_peer_key(self, pairing_id: bytes):
        if pairing_id.decode() not in self.peers:
            return
        return bytes.fromhex(self.peers[pairing_id.decode()]['key'])

    def connect(self):
        self.connected = True

    def disconnect(self):
        self.connected = False

        #print(self.sessions[self.session_id])
        #del self.sessions[self.session_id]['controller_to_accessory_key']
        #del self.sessions[self.session_id]['accessory_to_controller_key']


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

    def write_value(self, value):
        device = self.service.device
        session = device.sessions[device.session_id]

        if 'controller_to_accessory_key' in session:
            c2a_key = session['controller_to_accessory_key']
            cnt_bytes = session['controller_to_accessory_count'].to_bytes(8, byteorder='little')
            value = chacha20_aead_decrypt(b'', c2a_key, cnt_bytes, bytes([0, 0, 0, 0]), value)
            session['controller_to_accessory_count'] += 1

        assert value[0] == 0
        opcode = value[1]
        tid = value[2]
        cid = int.from_bytes(value[3:5], byteorder='little')
        length = int.from_bytes(value[5:7], byteorder='little')
        payload = value[7:]

        if opcode == HapBleOpCodes.CHAR_WRITE:
            new_value = dict(TLV.decode_bytes(payload))
            self.char.set_value_from_ble(new_value[1])

            response = bytearray([0x02, tid, 0x00])
            self.append_value_secure(bytes(response))

        elif opcode == HapBleOpCodes.CHAR_READ:
            value = self.char.get_value_for_ble()
            #÷÷÷
            value = TLV.encode_list([(TLV.kTLVHAPParamValue, value)])

            response = bytearray([0x02, tid, 0x00])
            tlv = len(value).to_bytes(2, byteorder='little') + value
            response.extend(tlv)
            self.append_value_secure(bytes(response))

        elif opcode == HapBleOpCodes.CHAR_SIG_READ:
            response = bytearray([0x02, tid, 0x00])

            import uuid
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
                (TLV.kTLVHAPParamHAPCharacteristicPropertiesDescriptor, b'\x00'),
                (TLV.kTLVHAPParamGATTPresentationFormatDescriptor, gatt_fmt),
                (TLV.kTLVHAPParamCharacteristicType, char_type),
                (TLV.kTLVHAPParamServiceInstanceId, self.service.service.iid.to_bytes(length=8, byteorder='little')),
                (TLV.kTLVHAPParamServiceType, service_type),
            ]

            tlv = TLV.encode_list(data)
            response.extend(len(tlv).to_bytes(2, byteorder='little') + tlv)
            self.append_value_secure(bytes(response))
        else:
            raise RuntimeError('Fake does not implement opcode %s' % opcode)

    def append_value(self, value):
        self.values.append(value)

    def append_value_secure(self, value):
        device = self.service.device
        session = device.sessions[device.session_id]
        if 'accessory_to_controller_key' in session:
            a2c_key = session['accessory_to_controller_key']
            cnt_bytes = session['accessory_to_controller_count'].to_bytes(8, byteorder='little')
            ciper_and_mac = chacha20_aead_encrypt(b'', a2c_key, cnt_bytes, bytes([0, 0, 0, 0]), value)
            session['accessory_to_controller_count'] += 1
            value = ciper_and_mac[0] + ciper_and_mac[1]

        self.append_value(value)

    def read_value(self):
        if not self.values:
            return b''

        return self.values.pop(0)


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
        print(message % args)

    def log_error(self, message, *args):
        print(message % args)

    def send_error(self, *args):
        assert False, 'sent error'

    def publish_device(self, *args):
        pass

    def send_error_reply(self, state, error):
        d_res = [
            (TLV.kTLVType_State, state),
            (TLV.kTLVType_Error, error)
        ]
        self._send_response_tlv(d_res)

    def _send_response_tlv(self, d_res, close=False, status=None):
        result_bytes = TLV.encode_list(d_res)

        outer = TLV.encode_list([
            (TLV.kTLVHAPParamValue, result_bytes),
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

    def add_peer(self, *args):
        pass

    def write_value(self, value):
        assert value[0] == 0
        opcode = value[1]
        tid = value[2]
        cid = int.from_bytes(value[3:5], byteorder='little')
        length = int.from_bytes(value[5:7], byteorder='little')

        if opcode == 2:
            outer = dict(TLV.decode_bytes(value[7:]))
            assert outer[TLV.kTLVHAPParamParamReturnResponse] == b'\x01'

            value = self.rh.process_setup(value[2], outer[TLV.kTLVHAPParamValue])
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
        tid = value[2]
        cid = int.from_bytes(value[3:5], byteorder='little')
        length = int.from_bytes(value[5:7], byteorder='little')

        if opcode == 2:
            outer = dict(TLV.decode_bytes(value[7:]))
            assert outer[TLV.kTLVHAPParamParamReturnResponse] == b'\x01'

            value = self.rh.process_verify(value[2], outer[TLV.kTLVHAPParamValue])
            self.values.append(value)
        else:
            super().write_value(value)


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


class TestBLEController(unittest.TestCase):

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
        manager.devices['00:00:00:00:00'] = Device(a)

        with mock.patch('homekit.controller.ble_impl.device.DeviceManager') as m:
            m.return_value = manager
            c.perform_pairing_ble('test-pairing', '00:00:00:00:00', '111-11-111')

        assert c.pairings['test-pairing'].pairing_data['Connection'] == 'BLE'

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
        manager.devices['00:00:00:00:00'] = Device(a)

        with mock.patch('homekit.controller.ble_impl.device.DeviceManager') as m:
            with mock.patch('homekit.controller.ble_implementation.DeviceManager') as m2:
                m.return_value = manager
                m2.return_value = manager
                c.perform_pairing_ble('test-pairing', '00:00:00:00:00', '111-11-111')
                accessories = c.pairings['test-pairing'].list_accessories_and_characteristics()

        assert accessories == [
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
                            }
                        ],
                        "iid": 11,
                        "type": "00000055-0000-1000-8000-0026BB765291"
                    }
                ]
            }
        ]

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
        d = manager.devices['00:00:00:00:00'] = Device(a)

        with mock.patch('homekit.controller.ble_impl.device.DeviceManager') as m1:
            with mock.patch('homekit.controller.ble_implementation.DeviceManager') as m2:
                m1.return_value = manager
                m2.return_value = manager
                c.perform_pairing_ble('test-pairing', '00:00:00:00:00', '111-11-111')
                c.pairings['test-pairing'].list_accessories_and_characteristics()
                result = c.pairings['test-pairing'].get_characteristics([
                    (1, 4),
                ])

        assert result == {
            (1, 4): {
                "value": "TestCo",
            }
        }

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
        d = manager.devices['00:00:00:00:00'] = Device(a)

        with mock.patch('homekit.controller.ble_impl.device.DeviceManager') as m1:
            with mock.patch('homekit.controller.ble_implementation.DeviceManager') as m2:
                m1.return_value = manager
                m2.return_value = manager
                c.perform_pairing_ble('test-pairing', '00:00:00:00:00', '111-11-111')
                c.pairings['test-pairing'].list_accessories_and_characteristics()

                result = c.pairings['test-pairing'].put_characteristics([
                    (1, 10, True),
                ])
                assert result == {}
                assert a.services[1].characteristics[0].get_value() == True

                result = c.pairings['test-pairing'].put_characteristics([
                    (1, 10, False),
                ])
                assert result == {}
                assert a.services[1].characteristics[0].get_value() == False

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
        d = manager.devices['00:00:00:00:00'] = Device(a)

        with mock.patch('homekit.controller.ble_impl.device.DeviceManager') as m1:
            with mock.patch('homekit.controller.ble_implementation.DeviceManager') as m2:
                m1.return_value = manager
                m2.return_value = manager
                c.perform_pairing_ble('test-pairing', '00:00:00:00:00', '111-11-111')
                c.pairings['test-pairing'].list_accessories_and_characteristics()

                assert a.services[0].characteristics[0].value == None
                c.pairings['test-pairing'].identify()
                assert a.services[0].characteristics[0].value == True

