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

import logging
import time
import atexit
import dbus

from homekit.exceptions import AccessoryNotFoundError

from . import gatt
from .manufacturer_data import parse_manufacturer_specific

# 0x004c is the Company Identifier code for Apple Inc. (see Chapter 6.4.2.2 of the spec on page 124)
COID_APPLE = 0x004c


logger = logging.getLogger(__name__)


class Device(gatt.Device):
    """
    A subclass of gatt.Device that makes it a little easier to use for
    implementing BLE HAP. This class only contains thin wrappers on top of
    Device, such as for decoding manufacturer data and ensuring services are
    resolved after connecting to a device. All HAP protocol details are handled
    at a higher level.

    The `name` field fetches the name of the device according to BlueZ's
    `Alias` property. (Note that direct use of the BlueZ `Name` field seems to
    be discouraged).

    The `homekit_discover_data` field contains the decoded ManufacturerData
    retrieved from BlueZ.
    """

    def __init__(self, *args, **kwargs):
        gatt.Device.__init__(self, *args, **kwargs, managed=False)

        self.name = self._properties.Get('org.bluez.Device1', 'Alias')
        self.homekit_discovery_data = self.get_homekit_discovery_data()

    def get_homekit_discovery_data(self):
        """
        Retrieve and decode the latest ManufacturerData from BlueZ for a
        HomeKit device
        """
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

        parsed = parse_manufacturer_specific(mfr_data[COID_APPLE])

        if parsed['type'] != 'HomeKit':
            return {}

        return parsed

    def connect(self):
        """
        Establishes a connection to a BLE device. This function does not return
        until the services exposed by the device are fully resolved.

        Eventually the connection will timeout and an `AccessoryNotFound` error
        will be raised.
        """
        super().connect()

        try:
            if not self.services:
                logger.debug('waiting for services to be resolved')
                for i in range(20):
                    if self.is_services_resolved():
                        break
                    time.sleep(1)
                else:
                    raise AccessoryNotFoundError('Unable to resolve device services + characteristics')

                # This is called automatically when the mainloop is running, but we
                # want to avoid running it and blocking for an indeterminate amount of time.
                logger.debug('enumerating resolved services')
                self.services_resolved()
        except dbus.exceptions.DBusException:
            raise AccessoryNotFoundError('Unable to resolve device services + characteristics')

    def characteristic_read_value_failed(self, characteristic, error):
        logger.debug('read failed: %s %s', characteristic, error)

    def characteristic_write_value_succeeded(self, characteristic):
        logger.debug('write success: %s', characteristic)

    def characteristic_write_value_failed(self, characteristic, error):
        logger.debug('write failed: %s %s', characteristic, error)


class DeviceManager(gatt.DeviceManager):

    discover_callback = None
    Device = Device

    def __init__(self, adapter):
        super().__init__(adapter)

        # save the old power state of the Bluetooth LE adapter to be able to restore it after
        # the program ends
        atexit.register(self.cleanup)
        self.old_powerstate = self.is_adapter_powered
        self.adapter = adapter
        if not self.old_powerstate:
            logger.debug('Powering on adapter "%s"' % adapter)
            self.is_adapter_powered = True

    def make_device(self, mac_address):
        return self.Device(mac_address=mac_address, manager=self)

    def cleanup(self):
        # restore the old power state
        if not self.old_powerstate:
            logger.debug('restoring power state adapter "%s"' % self.adapter)
            self.is_adapter_powered = self.old_powerstate
