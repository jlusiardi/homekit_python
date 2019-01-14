import abc
import base64
import binascii
import logging
from distutils.util import strtobool
import threading
import time

import dbus

from homekit.model import Categories
from homekit.protocol.tlv import TLV, TlvParseException
from homekit.exceptions import FormatError
from homekit.model.characteristics import CharacteristicFormats
from staging import gatt


def hci_adapter_exists_and_supports_bluetooth_le(adapter_name):
    """
    This checks via dbus if an bluez adapter with the given name exists and if so checks if there is an interface named
    'org.bluez.LEAdvertisingManager1'. This seems to be a bit flaky but the best i've got.

    :param adapter: the bluetooth adapter to be used (hci0, hci1, ...)
    :return: True if the adapter exists and supports BLE, False otherwise
    """
    bus = dbus.SystemBus()
    manager = dbus.Interface(bus.get_object('org.bluez', '/'), 'org.freedesktop.DBus.ObjectManager')
    managed_objects = manager.GetManagedObjects()
    for path in managed_objects:
        ifaces = managed_objects[path]
        adapter = ifaces.get('org.bluez.Adapter1')
        if adapter is None:
            continue
        if not adapter_name or adapter_name == adapter['Address'] or path.endswith(adapter_name):
            return 'org.bluez.LEAdvertisingManager1' in ifaces
    return False


class AbstractPairing(abc.ABC):

    def _get_pairing_data(self):
        """
        This method returns the internal pairing data. DO NOT mess around with it.

        :return: a dict containing the data
        """
        return self.pairing_data

    @abc.abstractmethod
    def close(self):
        """
        Close the pairing's communications. This closes the session.
        """
        pass

    @abc.abstractmethod
    def list_accessories_and_characteristics(self):
        """
        This retrieves a current set of accessories and characteristics behind this pairing.

        :return: the accessory data as described in the spec on page 73 and following
        :raises AccessoryNotFoundError: if the device can not be found via zeroconf
        """
        pass

    @abc.abstractmethod
    def list_pairings(self):
        """
        This method returns all pairings of a HomeKit accessory. This always includes the local controller and can only
        be done by an admin controller.

        The keys in the resulting dicts are:
         * pairingId: the pairing id of the controller
         * publicKey: the ED25519 long-term public key of the controller
         * permissions: bit value for the permissions
         * controllerType: either admin or regular

        :return: a list of dicts
        :raises: UnknownError: if it receives unexpected data
        :raises: UnpairedError: if the polled accessory is not paired
        """
        pass

    @abc.abstractmethod
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
        pass

    @abc.abstractmethod
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
        pass

    @abc.abstractmethod
    def get_events(self, characteristics, callback_fun, max_events=-1, max_seconds=-1):
        """
        This function is called to register for events on characteristics and receive them. Each time events are
        received a call back function is invoked. By that the caller gets information about the events.

        The characteristics are identified via their proper accessory id (aid) and instance id (iid).

        The call back function takes a list of 3-tupels of aid, iid and the value, e.g.:
          [(1, 9, 26.1), (1, 10, 30.5)]

        If the input contains characteristics without the event permission or any other error, the function will return
        a dict containing tupels of aid and iid for each requested characteristic with error. Those who would have
        worked are not in the result.

        :param characteristics: a list of 2-tupels of accessory id (aid) and instance id (iid)
        :param callback_fun: a function that is called each time events were recieved
        :param max_events: number of reported events, default value -1 means unlimited
        :param max_seconds: number of seconds to wait for events, default value -1 means unlimited
        :return: a dict mapping 2-tupels of aid and iid to dicts with status and description, e.g.
                 {(1, 37): {'description': 'Notification is not supported for characteristic.', 'status': -70406}}
        """
        pass

    @abc.abstractmethod
    def identify(self):
        """
        This call can be used to trigger the identification of a paired accessory. A successful call should
        cause the accessory to perform some specific action by which it can be distinguished from the others (blink a
        LED for example).

        It uses the identify characteristic as described on page 152 of the spec.

        :return True, if the identification was run, False otherwise
        """
        pass


def check_convert_value(val, target_type):
    """
    Checks if the given value is of the given type or is convertible into the type. If the value is not convertible, a
    HomeKitTypeException is thrown.

    :param val: the original value
    :param target_type: the target type of the conversion
    :return: the converted value
    :raises FormatError: if the input value could not be converted to the target type
    """
    if target_type == CharacteristicFormats.bool:
        try:
            val = strtobool(str(val))
        except ValueError:
            raise FormatError('"{v}" is no valid "{t}"!'.format(v=val, t=target_type))
    if target_type in [CharacteristicFormats.uint64, CharacteristicFormats.uint32,
                       CharacteristicFormats.uint16, CharacteristicFormats.uint8,
                       CharacteristicFormats.int]:
        try:
            val = int(val)
        except ValueError:
            raise FormatError('"{v}" is no valid "{t}"!'.format(v=val, t=target_type))
    if target_type == CharacteristicFormats.float:
        try:
            val = float(val)
        except ValueError:
            raise FormatError('"{v}" is no valid "{t}"!'.format(v=val, t=target_type))
    if target_type == CharacteristicFormats.data:
        try:
            base64.decodebytes(val.encode())
        except binascii.Error:
            raise FormatError('"{v}" is no valid "{t}"!'.format(v=val, t=target_type))
    if target_type == CharacteristicFormats.tlv8:
        try:
            tmp_bytes = base64.decodebytes(val.encode())
            TLV.decode_bytes(tmp_bytes)
        except (binascii.Error, TlvParseException):
            raise FormatError('"{v}" is no valid "{t}"!'.format(v=val, t=target_type))
    return val


class DelayedExecution(threading.Thread):
    """
    Execute a function with a given delay using a thread in the background.

    Typical usage:
        de = DelayedExecution(some_func, 10)
        de.start()
    """

    def __init__(self, func, timeout):
        """
        Create a DelayedExecution for the given function. The function will be executed after the given timeout (in
        seconds, fractions of seconds are also possible).
        :param func: the function to call
        :param timeout: the time out in seconds
        """
        threading.Thread.__init__(self)
        self.timeout = timeout
        self.function = func

    def run(self):
        time.sleep(self.timeout)
        self.function()


def parse_manufacturer_specific_data(input_data):
    """
    Parse the manufacturer specific data as returned via Bluez ManufacturerData. This skips the data for LEN, ADT and
    CoID as specified in Chapter 6.4.2.2 of the spec on page 124. Data therefore starts at TY (must be 0x06).

    :param input_data: manufacturer specific data as bytes
    :return: a dict containing the type (key 'type', value 'HomeKit'), the status flag (key 'sf'), human readable
             version of the status flag (key 'flags'), the device id (key 'device_id'), the accessory category
             identifier (key 'acid'), human readable version of the category (key 'category'), the global state number
             (key 'gsn'), the configuration number (key 'cn') and the compatible version (key 'cv')
    """
    logging.debug('manufacturer specific data: %s', input_data.hex())

    # the type must be 0x06 as defined on page 124 table 6-29
    ty = input_data[0]
    input_data = input_data[1:]
    if ty == 0x06:
        ty = 'HomeKit'

        ail = input_data[0]
        logging.debug('advertising interval %s', '{0:02x}'.format(ail))
        length = ail & 0b00011111
        if length != 13:
            logging.debug('error with length of manufacturer data')
        input_data = input_data[1:]

        sf = input_data[0]
        if sf == 0:
            flags = 'paired'
        elif sf == 1:
            flags = 'unpaired'
        else:
            flags = 'error'
        input_data = input_data[1:]

        device_id = (':'.join(input_data[:6].hex()[0 + i:2 + i] for i in range(0, 12, 2))).upper()
        input_data = input_data[6:]

        acid = int.from_bytes(input_data[:2], byteorder='little')
        input_data = input_data[2:]

        gsn = int.from_bytes(input_data[:2], byteorder='little')
        input_data = input_data[2:]

        cn = input_data[0]
        input_data = input_data[1:]

        cv = input_data[0]
        input_data = input_data[1:]
        if len(input_data) > 0:
            logging.debug('remaining data: %s', input_data.hex())
        return {'type': ty, 'sf': sf, 'flags': flags, 'device_id': device_id, 'acid': acid, 'gsn': gsn, 'cn': cn,
                'cv': cv, 'category': Categories[int(acid)]}

    return {'manufacturer': 'apple', 'type': ty}


# 0x004c is the Company Identifier code for Apple Inc. (see Chapter 6.4.2.2 of the spec on page 124)
COID_APPLE = 0x004c


class HomekitDiscoveryDevice(gatt.Device):
    """
    Extension to gatt.Device that uses dbus to read manufacturer specific data from bluez devices and parses this data.
    The data will be accessible via the field `homekit_discovery_data`. The device's name is stored in the field `name`.
    """

    def __init__(self, *args, **kwargs):
        gatt.Device.__init__(self, *args, **kwargs, managed=False)

        self.name = self._properties.Get('org.bluez.Device1', 'Alias')
        self.homekit_discovery_data = self._get_homekit_discovery_data()

    def _get_homekit_discovery_data(self):

        try:
            mfr_data = self._properties.Get('org.bluez.Device1', 'ManufacturerData')
        except dbus.exceptions.DBusException as e:
            if e.get_dbus_name() == 'org.freedesktop.DBus.Error.InvalidArgs':
                return {}
            raise

        # convert from dbus.Dictionary({dbus.UInt16(...): dbus.Array([dbus.Byte(...),...])}) to a dict(int: bytes)
        mfr_data = dict((int(k), bytes(bytearray(v))) for (k, v) in mfr_data.items())

        if COID_APPLE not in mfr_data:
            return {}

        parsed = parse_manufacturer_specific_data(mfr_data[COID_APPLE])

        if parsed['type'] != 'HomeKit':
            return {}

        return parsed


class HomekitDiscoveryDeviceManager(gatt.DeviceManager):
    """
    Extension to gatt.DeviceManager that checks if a new device is a HomeKit Accessory and tries to parse its HomeKit
    specific data.
    """

    def make_device(self, mac_address):
        homekit_device = HomekitDiscoveryDevice(mac_address=mac_address, manager=self)
        if not homekit_device.homekit_discovery_data:
            return
        self._manage_device(homekit_device)
        return homekit_device

    def get_devices(self):
        """
        Returns all known Bluetooth devices with explicit update.
        """
        return self._devices.values()
