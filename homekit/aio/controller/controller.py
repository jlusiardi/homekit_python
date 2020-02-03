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

import json
from json.decoder import JSONDecodeError
import logging
import re

from homekit.exceptions import AccessoryNotFoundError, ConfigLoadingError, \
    ConfigSavingError, TransportNotSupportedError, MalformedPinError
from homekit.tools import IP_TRANSPORT_SUPPORTED, BLE_TRANSPORT_SUPPORTED

if IP_TRANSPORT_SUPPORTED:
    from .ip import IpDiscovery, IpPairing
    from .ip.zeroconf import async_discover_homekit_devices


class Controller(object):
    """
    This class represents a HomeKit controller (normally your iPhone or iPad).
    """

    def __init__(self, ble_adapter='hci0'):
        """
        Initialize an empty controller. Use 'load_data()' to load the pairing data.

        :param ble_adapter: the bluetooth adapter to be used (defaults to hci0)
        """
        self.pairings = {}
        self.ble_adapter = ble_adapter
        self.logger = logging.getLogger('homekit.controller.Controller')

    async def discover_ip(self, max_seconds=10):
        """
        Perform a Bonjour discovery for HomeKit accessory. The discovery will last for the given amount of seconds. The
        result will be a list of dicts. The keys of the dicts are:
         * name: the Bonjour name of the HomeKit accessory (i.e. Testsensor1._hap._tcp.local.)
         * address: the IP address of the accessory
         * port: the used port
         * c#: the configuration number (required)
         * ff / flags: the numerical and human readable version of the feature flags (supports pairing or not, see table
                       5-8 page 69)
         * id: the accessory's pairing id (required)
         * md: the model name of the accessory (required)
         * pv: the protocol version
         * s#: the current state number (required)
         * sf / statusflags: the status flag (see table 5-9 page 70)
         * ci / category: the category identifier in numerical and human readable form. For more information see table
                        12-3 page 254 or homekit.Categories (required)

        IMPORTANT:
        This method will ignore all HomeKit accessories that exist in _hap._tcp domain but fail to have all required
        TXT record keys set.

        :param max_seconds: how long should the Bonjour service browser do the discovery (default 10s). See sleep for
                            more details
        :return: a list of dicts as described above
        """
        if not IP_TRANSPORT_SUPPORTED:
            raise TransportNotSupportedError('IP')
        devices = await async_discover_homekit_devices(max_seconds)
        tmp = []
        for device in devices:
            tmp.append(IpDiscovery(self, device))
        return tmp

    async def find_ip_by_device_id(self, device_id, max_seconds=10):
        results = await self.discover_ip(max_seconds=max_seconds)
        for result in results:
            if result.device_id == device_id:
                return result
        raise AccessoryNotFoundError('No matching accessory found')

    @staticmethod
    async def discover_ble(max_seconds=10, adapter='hci0'):
        """
        Perform a Bluetooth LE discovery for HomeKit accessory. It will listen for Bluetooth LE advertisement events
        for the given amount of seconds. The result will be a list of dicts. The keys of the dicts are:
         * name: the model name of the accessory (required)
         * mac: the MAC address of the accessory (required)
         * sf / flags: the numerical and human readable version of the status flags (supports pairing or not, see table
                       6-32 page 125)
         * device_id: the accessory's device id (required)
         * acid / category: the category identifier in numerical and human readable form. For more information see table
                            12-3 page 254 or homekit.Categories (required)
         * gsn: Global State Number, increment on change of any characteristic, overflows at 65535.
         * cn: the configuration number (required)
         * cv: the compatible version

        :param max_seconds: how long should the Bluetooth LE discovery should be performed (default 10s). See sleep for
                            more details
        :param adapter: the bluetooth adapter to be used (defaults to hci0)
        :return: a list of dicts as described above
        """
        raise TransportNotSupportedError('BLE')

    async def shutdown(self):
        """
        Shuts down the controller by closing all connections that might be held open by the pairings of the controller.
        """
        for p in self.pairings:
            await self.pairings[p].close()

    def get_pairings(self):
        """
        Returns a dict containing all pairings known to the controller.

        :return: the dict maps the aliases to Pairing objects
        """
        return self.pairings

    def load_data(self, filename):
        """
        Loads the pairing data of the controller from a file.

        :param filename: the file name of the pairing data
        :raises ConfigLoadingError: if the config could not be loaded. The reason is given in the message.
        """
        try:
            with open(filename, 'r') as input_fp:
                data = json.load(input_fp)
                for pairing_id in data:

                    if 'Connection' not in data[pairing_id]:
                        # This is a pre BLE entry in the file with the pairing data, hence it is for an IP based
                        # accessory. So we set the connection type (in case save data is used everything will be fine)
                        # and also issue a warning
                        data[pairing_id]['Connection'] = 'IP'
                        self.logger.warning(
                            'Loaded pairing for %s with missing connection type. Assume this is IP based.', pairing_id)

                    if data[pairing_id]['Connection'] == 'IP':
                        if not IP_TRANSPORT_SUPPORTED:
                            raise TransportNotSupportedError('IP')
                        self.pairings[pairing_id] = IpPairing(data[pairing_id])
                    elif data[pairing_id]['Connection'] == 'BLE':
                        if not BLE_TRANSPORT_SUPPORTED:
                            raise TransportNotSupportedError('BLE')
                        raise NotImplementedError('BLE support')
                    else:
                        # ignore anything else, issue warning
                        self.logger.warning('could not load pairing %s of type "%s"', pairing_id,
                                            data[pairing_id]['Connection'])
        except PermissionError:
            raise ConfigLoadingError('Could not open "{f}" due to missing permissions'.format(f=filename))
        except JSONDecodeError:
            raise ConfigLoadingError('Cannot parse "{f}" as JSON file'.format(f=filename))
        except FileNotFoundError:
            raise ConfigLoadingError('Could not open "{f}" because it does not exist'.format(f=filename))

    def save_data(self, filename):
        """
        Saves the pairing data of the controller to a file.

        :param filename: the file name of the pairing data
        :raises ConfigSavingError: if the config could not be saved. The reason is given in the message.
        """
        data = {}
        for pairing_id in self.pairings:
            # package visibility like in java would be nice here
            data[pairing_id] = self.pairings[pairing_id]._get_pairing_data()
        try:
            with open(filename, 'w') as output_fp:
                json.dump(data, output_fp, indent='  ')
        except PermissionError:
            raise ConfigSavingError('Could not write "{f}" due to missing permissions'.format(f=filename))
        except FileNotFoundError:
            raise ConfigSavingError(
                'Could not write "{f}" because it (or the folder) does not exist'.format(f=filename))

    @staticmethod
    def check_pin_format(pin):
        """
        Checks the format of the given pin: XXX-XX-XXX with X being a digit from 0 to 9

        :raises MalformedPinError: if the validation fails
        """
        if not re.match(r'^\d\d\d-\d\d-\d\d\d$', pin):
            raise MalformedPinError('The pin must be of the following XXX-XX-XXX where X is a digit between 0 and 9.')

    async def remove_pairing(self, alias):
        """
        Remove a pairing between the controller and the accessory. The pairing data is delete on both ends, on the
        accessory and the controller.

        Important: no automatic saving of the pairing data is performed. If you don't do this, the accessory seems still
            to be paired on the next start of the application.

        :param alias: the controller's alias for the accessory
        :raises AuthenticationError: if the controller isn't authenticated to the accessory.
        :raises AccessoryNotFoundError: if the device can not be found via zeroconf
        :raises UnknownError: on unknown errors
        """
        if alias not in self.pairings:
            raise AccessoryNotFoundError('Alias "{a}" is not found.'.format(a=alias))

        pairing = self.pairings[alias]

        primary_pairing_id = pairing.pairing_data['iOSPairingId']
        await pairing.remove_pairing(primary_pairing_id)

        await pairing.close()

        del self.pairings[alias]
