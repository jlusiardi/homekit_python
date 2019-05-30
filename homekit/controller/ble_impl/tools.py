import logging

import dbus
import gatt

from homekit.model import Categories


def _get_hci_adapter(adapter_name):
    """
    Returns the DBus interfaces of the given adapter (if the adapter exists).

    :param adapter_name: the bluetooth adapter to be returned (hci0, hci1, ...)
    :return: the existing interfaces into DBus, None if the adapter does not exist.
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
            return ifaces
    return None


def hci_adapter_exists(adapter_name):
    """
    This checks via dbus if an bluez adapter with the given name exists.

    :param adapter_name: the bluetooth adapter to be used (hci0, hci1, ...)
    :return: True if the adapter exists, False otherwise
    """
    return _get_hci_adapter(adapter_name) is not None


def hci_adapter_exists_and_supports_bluetooth_le(adapter_name):
    """
    This checks via dbus if an bluez adapter with the given name exists and if so checks if there is an interface named
    'org.bluez.LEAdvertisingManager1'. This seems to be a bit flaky but the best i've got.

    :param adapter_name: the bluetooth adapter to be used (hci0, hci1, ...)
    :return: True if the adapter exists and supports BLE, False otherwise
    """
    ifaces = _get_hci_adapter(adapter_name)
    if ifaces:
        return 'org.bluez.LEAdvertisingManager1' in ifaces
    return False


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
