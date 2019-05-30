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

from .device import DeviceManager


class DiscoveryDeviceManager(DeviceManager):

    """
    Extension to gatt.DeviceManager that checks if a new device is a HomeKit
    Accessory and tries to parse its HomeKit specific data.
    """

    discover_callback = None

    def make_device(self, mac_address):
        """
        Should not need to call this directly when discovering devices.
        It is called by DeviceManager internals - we subclass it to make it
        ignore non-homekit devices.
        """
        device = super().make_device(mac_address=mac_address)
        if not device.homekit_discovery_data:
            return
        self._manage_device(device)
        if self.discover_callback:
            self.discover_callback(device)

    def start_discovery(self, callback=None):
        """
        Tells BlueZ to start notifying us of detected BLE devices.

        If `callback` is provided and the dbus mainloop is running then your
        function will be called every time a new device is discovered.
        """
        self.discover_callback = callback
        return super().start_discovery()

    def devices(self):
        # The standard implementation of devices causes a fresh of the dbus
        # objects which is not what we want at all
        return self._devices.values()
