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
