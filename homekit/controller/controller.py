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
import random
import uuid
import re

from homekit.exceptions import AccessoryNotFoundError, ConfigLoadingError, UnknownError, \
    AuthenticationError, ConfigSavingError, AlreadyPairedError, TransportNotSupportedError, MalformedPinError
from homekit.protocol.tlv import TLV
from homekit.http_impl import HomeKitHTTPConnection
from homekit.protocol.statuscodes import HapStatusCodes
from homekit.protocol import perform_pair_setup_part1, perform_pair_setup_part2, create_ip_pair_setup_write
from homekit.model.services.service_types import ServicesTypes
from homekit.model.characteristics.characteristic_types import CharacteristicsTypes
from homekit.protocol.opcodes import HapBleOpCodes
from homekit.tools import IP_TRANSPORT_SUPPORTED, BLE_TRANSPORT_SUPPORTED
from homekit.controller.additional_pairing import AdditionalPairing

if BLE_TRANSPORT_SUPPORTED:
    from homekit.controller.ble_impl import BlePairing, BleSession, find_characteristic_by_uuid, \
        create_ble_pair_setup_write
    from .ble_impl.discovery import DiscoveryDeviceManager

if IP_TRANSPORT_SUPPORTED:
    from homekit.zeroconf_impl import discover_homekit_devices, find_device_ip_and_port
    from homekit.controller.ip_implementation import IpPairing, IpSession


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

    @staticmethod
    def discover(max_seconds=10):
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
        return discover_homekit_devices(max_seconds)

    @staticmethod
    def discover_ble(max_seconds=10, adapter='hci0'):
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
        if not BLE_TRANSPORT_SUPPORTED:
            raise TransportNotSupportedError('BLE')
        manager = DiscoveryDeviceManager(adapter)
        manager.start_discovery()
        manager.set_timeout(max_seconds * 1000)
        manager.run()

        result = []
        for discovered_device in manager.devices():
            data = discovered_device.homekit_discovery_data
            r = {
                'name': discovered_device.name,
                'mac': discovered_device.mac_address,
                'acid': data['acid'],
                'category': data['category'],
                'device_id': data['device_id'],
                'cv': data['cv'],
                'cn': data['cn'],
                'gsn': data['gsn'],
                'sf': data['sf'],
                'flags': data['flags']
            }
            result.append(r)
        return result

    @staticmethod
    def identify(accessory_id):
        """
        This call can be used to trigger the identification of an accessory, that was not yet paired. A successful call
        should cause the accessory to perform some specific action by which it can be distinguished from others (blink a
        LED for example).

        It uses the /identify url as described on page 88 of the spec.

        :param accessory_id: the accessory's pairing id (e.g. retrieved via discover)
        :raises AccessoryNotFoundError: if the accessory could not be looked up via Bonjour
        :raises AlreadyPairedError: if the accessory is already paired
        """
        if not IP_TRANSPORT_SUPPORTED:
            raise TransportNotSupportedError('IP')
        connection_data = find_device_ip_and_port(accessory_id)
        if connection_data is None:
            raise AccessoryNotFoundError('Cannot find accessory with id "{i}".'.format(i=accessory_id))

        conn = HomeKitHTTPConnection(connection_data['ip'], port=connection_data['port'])
        conn.request('POST', '/identify')
        resp = conn.getresponse()

        # spec says status code 400 on any error (page 88). It also says status should be -70401 (which is "Request
        # denied due to insufficient privileges." table 5-12 page 80) but this sounds odd.
        if resp.code == 400:
            data = json.loads(resp.read().decode())
            code = data['status']
            conn.close()
            raise AlreadyPairedError(
                'identify failed because: {reason} ({code}).'.format(reason=HapStatusCodes[code],
                                                                     code=code))
        conn.close()

    @staticmethod
    def identify_ble(accessory_mac, adapter='hci0'):
        """
        This call can be used to trigger the identification of an accessory, that was not yet paired. A successful call
        should cause the accessory to perform some specific action by which it can be distinguished from others (blink a
        LED for example).

        It uses the /identify url as described on page 88 of the spec.

        :param accessory_mac: the accessory's mac address (e.g. retrieved via discover)
        :raises AccessoryNotFoundError: if the accessory could not be looked up via Bonjour
        :param adapter: the bluetooth adapter to be used (defaults to hci0)
        :raises AlreadyPairedError: if the accessory is already paired
        """
        if not BLE_TRANSPORT_SUPPORTED:
            raise TransportNotSupportedError('BLE')
        from .ble_impl.device import DeviceManager
        manager = DeviceManager(adapter)
        device = manager.make_device(accessory_mac)
        device.connect()

        disco_info = device.get_homekit_discovery_data()
        if disco_info.get('flags', 'unknown') == 'paired':
            raise AlreadyPairedError(
                'identify of {mac_address} failed not allowed as device already paired'.format(
                    mac_address=accessory_mac),
            )

        identify, identify_iid = find_characteristic_by_uuid(
            device,
            ServicesTypes.ACCESSORY_INFORMATION_SERVICE,
            CharacteristicsTypes.IDENTIFY,
        )

        if not identify:
            raise AccessoryNotFoundError(
                'Device with address {mac_address} exists but did not find IDENTIFY characteristic'.format(
                    mac_address=accessory_mac)
            )

        value = TLV.encode_list([
            (1, b'\x01')
        ])
        body = len(value).to_bytes(length=2, byteorder='little') + value

        tid = random.randrange(0, 255)

        request = bytearray([0x00, HapBleOpCodes.CHAR_WRITE, tid])
        request.extend(identify_iid.to_bytes(length=2, byteorder='little'))
        request.extend(body)

        identify.write_value(request)
        response = bytearray(identify.read_value())

        if not response or not response[2] == 0x00:
            raise UnknownError('Unpaired identify failed')

        return True

    def shutdown(self):
        """
        Shuts down the controller by closing all connections that might be held open by the pairings of the controller.
        """
        for p in self.pairings:
            self.pairings[p].close()

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
        :raises TransportNotSupportedError: if the dependencies for the selected transport are not installed
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
                        self.pairings[pairing_id] = BlePairing(data[pairing_id], self.ble_adapter)
                    elif data[pairing_id]['Connection'] == 'ADDITIONAL_PAIRING':
                        self.pairings[pairing_id] = AdditionalPairing(data[pairing_id])
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

    def perform_pairing(self, alias, accessory_id, pin):
        """
        This performs a pairing attempt with the IP accessory identified by its id.

        Accessories can be found via the discover method. The id field is the accessory's id for the second parameter.

        The required pin is either printed on the accessory or displayed. Must be a string of the form 'XXX-YY-ZZZ'.

        Important: no automatic saving of the pairing data is performed. If you don't do this, the information is lost
            and you have to reset the accessory!

        :param alias: the alias for the accessory in the controllers data
        :param accessory_id: the accessory's id
        :param pin: function to return the accessory's pin
        :raises AccessoryNotFoundError: if no accessory with the given id can be found
        :raises AlreadyPairedError: if the alias was already used
        :raises UnavailableError: if the device is already paired
        :raises MaxTriesError: if the device received more than 100 unsuccessful attempts
        :raises BusyError: if a parallel pairing is ongoing
        :raises AuthenticationError: if the verification of the device's SRP proof fails
        :raises MaxPeersError: if the device cannot accept an additional pairing
        :raises UnavailableError: on wrong pin
        :raises MalformedPinError: if the pin is malformed
        """
        Controller.check_pin_format(pin)
        finish_pairing = self.start_pairing(alias, accessory_id)
        return finish_pairing(pin)

    def start_pairing(self, alias, accessory_id):
        """
        This starts a pairing attempt with the IP accessory identified by its id.
        It returns a callable (finish_pairing) which you must call with the pairing pin.

        Accessories can be found via the discover method. The id field is the accessory's id for the second parameter.

        The required pin is either printed on the accessory or displayed. Must be a string of the form 'XXX-YY-ZZZ'. If
        this format is not used, a MalformedPinError is raised.

        Important: no automatic saving of the pairing data is performed. If you don't do this, the information is lost
            and you have to reset the accessory!

        :param alias: the alias for the accessory in the controllers data
        :param accessory_id: the accessory's id
        :param pin: function to return the accessory's pin
        :raises AccessoryNotFoundError: if no accessory with the given id can be found
        :raises AlreadyPairedError: if the alias was already used
        :raises UnavailableError: if the device is already paired
        :raises MaxTriesError: if the device received more than 100 unsuccessful attempts
        :raises BusyError: if a parallel pairing is ongoing
        :raises AuthenticationError: if the verification of the device's SRP proof fails
        :raises MaxPeersError: if the device cannot accept an additional pairing
        :raises UnavailableError: on wrong pin
        """
        if not IP_TRANSPORT_SUPPORTED:
            raise TransportNotSupportedError('IP')
        if alias in self.pairings:
            raise AlreadyPairedError('Alias "{a}" is already paired.'.format(a=alias))

        connection_data = find_device_ip_and_port(accessory_id)
        if connection_data is None:
            raise AccessoryNotFoundError('Cannot find accessory with id "{i}".'.format(i=accessory_id))
        conn = HomeKitHTTPConnection(connection_data['ip'], port=connection_data['port'])

        try:
            write_fun = create_ip_pair_setup_write(conn)
            salt, pub_key = perform_pair_setup_part1(write_fun)
        except Exception:
            conn.close()
            raise

        def finish_pairing(pin):
            Controller.check_pin_format(pin)
            try:
                pairing = perform_pair_setup_part2(pin, str(uuid.uuid4()), write_fun, salt, pub_key)
            finally:
                conn.close()
            pairing['AccessoryIP'] = connection_data['ip']
            pairing['AccessoryPort'] = connection_data['port']
            pairing['Connection'] = 'IP'
            self.pairings[alias] = IpPairing(pairing)

        return finish_pairing

    def perform_pairing_ble(self, alias, accessory_mac, pin, adapter='hci0'):
        """
        This performs a pairing attempt with the Bluetooth LE accessory identified by its mac address.

        Accessories can be found via the discover method. The mac field is the accessory's mac for the second parameter.

        The required pin is either printed on the accessory or displayed. Must be a string of the form 'XXX-YY-ZZZ'. If
        this format is not used, a MalformedPinError is raised.

        Important: no automatic saving of the pairing data is performed. If you don't do this, the information is lost
            and you have to reset the accessory!

        :param alias: the alias for the accessory in the controllers data
        :param accessory_mac: the accessory's mac address
        :param pin: function to return the accessory's pin
        :param adapter: the bluetooth adapter to be used (defaults to hci0)
        :raises MalformedPinError: if the pin is malformed
        # TODO add raised exceptions
        """
        Controller.check_pin_format(pin)
        finish_pairing = self.start_pairing_ble(alias, accessory_mac, adapter)
        return finish_pairing(pin)

    def start_pairing_ble(self, alias, accessory_mac, adapter='hci0'):
        """
        This starts a pairing attempt with the Bluetooth LE accessory identified by its mac address.
        It returns a callable (finish_pairing) which you must call with the pairing pin.

        Accessories can be found via the discover method. The mac field is the accessory's mac for the second parameter.

        The required pin is either printed on the accessory or displayed. Must be a string of the form 'XXX-YY-ZZZ'.

        Important: no automatic saving of the pairing data is performed. If you don't do this, the information is lost
            and you have to reset the accessory!

        :param alias: the alias for the accessory in the controllers data
        :param accessory_mac: the accessory's mac address
        :param adapter: the bluetooth adapter to be used (defaults to hci0)
        # TODO add raised exceptions
        """
        if not BLE_TRANSPORT_SUPPORTED:
            raise TransportNotSupportedError('BLE')
        if alias in self.pairings:
            raise AlreadyPairedError('Alias "{a}" is already paired.'.format(a=alias))

        from .ble_impl.device import DeviceManager
        manager = DeviceManager(adapter)
        device = manager.make_device(mac_address=accessory_mac)

        logging.debug('connecting to device')
        device.connect()
        logging.debug('connected to device')

        pair_setup_char, pair_setup_char_id = find_characteristic_by_uuid(device, ServicesTypes.PAIRING_SERVICE,
                                                                          CharacteristicsTypes.PAIR_SETUP)
        logging.debug('setup char: %s %s', pair_setup_char, pair_setup_char.service.device)

        write_fun = create_ble_pair_setup_write(pair_setup_char, pair_setup_char_id)
        salt, pub_key = perform_pair_setup_part1(write_fun)

        def finish_pairing(pin):
            Controller.check_pin_format(pin)
            pairing = perform_pair_setup_part2(pin, str(uuid.uuid4()), write_fun, salt, pub_key)

            pairing['AccessoryMAC'] = accessory_mac
            pairing['Connection'] = 'BLE'

            self.pairings[alias] = BlePairing(pairing, adapter)

        return finish_pairing

    def remove_pairing(self, alias, pairingId=None):
        """
        Remove a pairing between the controller and the accessory. The pairing data is delete on both ends, on the
        accessory and the controller.

        Important: no automatic saving of the pairing data is performed. If you don't do this, the accessory seems still
            to be paired on the next start of the application.

        :param alias: the controller's alias for the accessory
        :param pairingId: the pairing id to be removed
        :raises AuthenticationError: if the controller isn't authenticated to the accessory.
        :raises AccessoryNotFoundError: if the device can not be found via zeroconf
        :raises UnknownError: on unknown errors
        """
        # package visibility like in java would be nice here
        pairing_data = self.pairings[alias]._get_pairing_data()
        connection_type = pairing_data['Connection']
        if not pairingId:
            pairingIdToDelete = pairing_data['iOSPairingId']
        else:
            pairingIdToDelete = pairingId

        # Prepare the common (for IP and BLE) request data
        request_tlv = TLV.encode_list([
            (TLV.kTLVType_State, TLV.M1),
            (TLV.kTLVType_Method, TLV.RemovePairing),
            (TLV.kTLVType_Identifier, pairingIdToDelete.encode())
        ])

        if connection_type == 'IP':
            if not IP_TRANSPORT_SUPPORTED:
                raise TransportNotSupportedError('IP')
            session = IpSession(pairing_data)
            # decode is required because post needs a string representation
            response = session.post('/pairings', request_tlv)
            session.close()
            data = response.read()
            data = TLV.decode_bytes(data)
        elif connection_type == 'BLE':
            if not BLE_TRANSPORT_SUPPORTED:
                raise TransportNotSupportedError('BLE')
            inner = TLV.encode_list([
                (TLV.kTLVHAPParamParamReturnResponse, bytearray(b'\x01')),
                (TLV.kTLVHAPParamValue, request_tlv)
            ])

            body = len(inner).to_bytes(length=2, byteorder='little') + inner

            from .ble_impl.device import DeviceManager
            manager = DeviceManager(self.ble_adapter)
            device = manager.make_device(pairing_data['AccessoryMAC'])
            device.connect()

            logging.debug('resolved %d services', len(device.services))
            pair_remove_char, pair_remove_char_id = find_characteristic_by_uuid(device, ServicesTypes.PAIRING_SERVICE,
                                                                                CharacteristicsTypes.PAIRING_PAIRINGS)
            logging.debug('setup char: %s %s', pair_remove_char, pair_remove_char.service.device)

            session = BleSession(pairing_data, self.ble_adapter)
            response = session.request(pair_remove_char, pair_remove_char_id, HapBleOpCodes.CHAR_WRITE, body)
            data = TLV.decode_bytes(response[1])
        else:
            raise Exception('not implemented (neither IP nor BLE)')

        # act upon the response (the same is returned for IP and BLE accessories)
        # handle the result, spec says, if it has only one entry with state == M2 we unpaired, else its an error.
        logging.debug('response data: %s', data)
        if len(data) == 1 and data[0][0] == TLV.kTLVType_State and data[0][1] == TLV.M2:
            if not pairingId:
                del self.pairings[alias]
        else:
            if data[1][0] == TLV.kTLVType_Error and data[1][1] == TLV.kTLVError_Authentication:
                raise AuthenticationError('Remove pairing failed: missing authentication')
            else:
                raise UnknownError('Remove pairing failed: unknown error')
