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

"""
This module contains backports of upcoming gatt-python features that havent
been merged yet.

It should only contain code required for these feature and to enable those
features to work.

Right now this module contains:

 * https://github.com/getsenic/gatt-python/pull/36 (GATT Descriptors)
 * https://github.com/getsenic/gatt-python/pull/38 (Discovery timeouts)

This is to allow us to ship homekit_python even though upstream hasn't exposed
all the functionality we require.

Any homekit specific functionality that we don't plan to upstream should subclass
the classes in this module.
"""

import re
import logging
import dbus
import gatt
from gatt.gatt_linux import _error_from_dbus_error
from gi.repository import GObject

from homekit.controller.ble_impl.tools import hci_adapter_exists_and_supports_bluetooth_le, hci_adapter_exists
from homekit.exceptions import BluetoothAdapterError


class Descriptor:

    def __init__(self, characteristic, path, uuid):
        self.characteristic = characteristic
        self.uuid = uuid
        self._bus = characteristic._bus
        self._path = path
        self._object = self._bus.get_object('org.bluez', self._path)

    def read_value(self, offset=0):
        try:
            val = self._object.ReadValue(
                {'offset': dbus.UInt16(offset, variant_level=1)},
                dbus_interface='org.bluez.GattDescriptor1')
            return val
        except dbus.exceptions.DBusException as e:
            error = _error_from_dbus_error(e)
            self.service.device.descriptor_read_value_failed(self, error=error)


class Characteristic(gatt.Characteristic):

    def __init__(self, service, path, uuid):
        gatt.Characteristic.__init__(self, service, path, uuid)

        descriptor_regex = re.compile(self._path + '/desc[0-9abcdef]{4}$')
        self.descriptors = [
            Descriptor(self, desc[0], desc[1]['org.bluez.GattDescriptor1']['UUID'])
            for desc in self._object_manager.GetManagedObjects().items()
            if descriptor_regex.match(desc[0])
        ]


class Service(gatt.Service):

    def characteristics_resolved(self):
        self._disconnect_characteristic_signals()

        characteristics_regex = re.compile(self._path + '/char[0-9abcdef]{4}$')
        managed_characteristics = [
            char for char in self._object_manager.GetManagedObjects().items()
            if characteristics_regex.match(char[0])]
        self.characteristics = [Characteristic(
            service=self,
            path=c[0],
            uuid=c[1]['org.bluez.GattCharacteristic1']['UUID']) for c in managed_characteristics]

        self._connect_characteristic_signals()


class Device(gatt.Device):

    def services_resolved(self):
        self._disconnect_service_signals()

        services_regex = re.compile(self._device_path + '/service[0-9abcdef]{4}$')
        managed_services = [
            service for service in self._object_manager.GetManagedObjects().items()
            if services_regex.match(service[0])]
        self.services = [Service(
            device=self,
            path=service[0],
            uuid=service[1]['org.bluez.GattService1']['UUID']) for service in managed_services]

        self._connect_service_signals()


class DeviceManager(gatt.DeviceManager):

    def __init__(self, adapter_name='hci0'):
        """
        Creates a new DeviceManager but performs a check first to verify the adapter exists and supports
        Bluetooth LE.

        :param adapter_name: the name of the adapter (defaults to hci0)
        :raises BluetoothAdapterError: if either the adapter does not exist or lacks appropriate capabilities
        """
        self.logger = logging.getLogger('homekit.controller.ble')
        if not hci_adapter_exists(adapter_name):
            raise BluetoothAdapterError('Adapter "{a}" does not exist!'.format(a=adapter_name))
        if not hci_adapter_exists_and_supports_bluetooth_le(adapter_name):
            print('Adapter "{a}" seems not to support Bluetooth LE, the command might not function properly!'
                  .format(a=adapter_name))
        super().__init__(adapter_name)

    def set_timeout(self, timeout):
        GObject.timeout_add(timeout, self.stop)

    def make_device(self, mac_address):
        return Device(mac_address=mac_address, manager=self)
