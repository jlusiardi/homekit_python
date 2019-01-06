import json
from json.decoder import JSONDecodeError
import uuid
import logging

from homekit.zeroconf_impl import discover_homekit_devices, find_device_ip_and_port
from homekit.controller.ip_implementation import IpPairing, IpSession
from homekit.controller.ble_implementation import BlePairing, BleSession, find_characteristic_by_uuid, \
    create_ble_pair_setup_write, ResolvingManager
from homekit.exceptions import AccessoryNotFoundError, ConfigLoadingError, UnknownError, \
    AuthenticationError, ConfigSavingError, AlreadyPairedError
from homekit.protocol.tlv import TLV
from homekit.http_impl import HomeKitHTTPConnection
from homekit.protocol.statuscodes import HapStatusCodes
from homekit.protocol import perform_pair_setup, create_ip_pair_setup_write
from homekit.model.services.service_types import ServicesTypes
from homekit.model.characteristics.characteristic_types import CharacteristicsTypes
from homekit.protocol.opcodes import HapBleOpCodes


class Controller(object):
    """
    This class represents a HomeKit controller (normally your iPhone or iPad).
    """

    def __init__(self):
        """
        Initialize an empty controller. Use 'load_data()' to load the pairing data.
        """
        self.pairings = {}
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
         * sf: the status flag (see table 5-9 page 70)
         * ci / category: the category identifier in numerical and human readable form. For more information see table
                        12-3 page 254 or homekit.Categories (required)

        IMPORTANT:
        This method will ignore all HomeKit accessories that exist in _hap._tcp domain but fail to have all required
        TXT record keys set.

        :param max_seconds: how long should the Bonjour service browser do the discovery (default 10s). See sleep for
                            more details
        :return: a list of dicts as described above
        """
        return discover_homekit_devices(max_seconds)

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
    def identify_ble(accessory_mac):
        """
        This call can be used to trigger the identification of an accessory, that was not yet paired. A successful call
        should cause the accessory to perform some specific action by which it can be distinguished from others (blink a
        LED for example).

        It uses the /identify url as described on page 88 of the spec.

        :param accessory_mac: the accessory's mac address (e.g. retrieved via discover)
        :raises AccessoryNotFoundError: if the accessory could not be looked up via Bonjour
        :raises AlreadyPairedError: if the accessory is already paired
        """
        pass

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
                        self.pairings[pairing_id] = IpPairing(data[pairing_id])
                    elif data[pairing_id]['Connection'] == 'BLE':
                        self.pairings[pairing_id] = BlePairing(data[pairing_id])
                    else:
                        # ignore anything else, issue warning
                        self.logger.warning('could not load pairing %s of type "%s"', pairing_id,
                                            data[pairing_id]['Connection'])
        except PermissionError as e:
            raise ConfigLoadingError('Could not open "{f}" due to missing permissions'.format(f=filename))
        except JSONDecodeError as e:
            raise ConfigLoadingError('Cannot parse "{f}" as JSON file'.format(f=filename))
        except FileNotFoundError as e:
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
        except PermissionError as e:
            raise ConfigSavingError('Could not write "{f}" due to missing permissions'.format(f=filename))
        except FileNotFoundError as e:
            raise ConfigSavingError(
                'Could not write "{f}" because it (or the folder) does not exist'.format(f=filename))

    def perform_pairing(self, alias, accessory_id, pin):
        """
        This performs a pairing attempt with the IP accessory identified by its id.

        Accessories can be found via the discover method. The id field is the accessory's id for the second parameter.

        The required pin is either printed on the accessory or displayed. Must be a string of the form 'XXX-YY-ZZZ'.

        Important: no automatic saving of the pairing data is performed. If you don't do this, the information is lost
            and you have to reset the accessory!

        :param alias: the alias for the accessory in the controllers data
        :param accessory_id: the accessory's id
        :param pin: the accessory's pin
        :raises AccessoryNotFoundError: if no accessory with the given id can be found
        :raises AlreadyPairedError: if the alias was already used
        :raises UnavailableError: if the device is already paired
        :raises MaxTriesError: if the device received more than 100 unsuccessful attempts
        :raises BusyError: if a parallel pairing is ongoing
        :raises AuthenticationError: if the verification of the device's SRP proof fails
        :raises MaxPeersError: if the device cannot accept an additional pairing
        :raises UnavailableError: on wrong pin
        """
        if alias in self.pairings:
            raise AlreadyPairedError('Alias "{a}" is already paired.'.format(a=alias))

        connection_data = find_device_ip_and_port(accessory_id)
        if connection_data is None:
            raise AccessoryNotFoundError('Cannot find accessory with id "{i}".'.format(i=accessory_id))
        conn = HomeKitHTTPConnection(connection_data['ip'], port=connection_data['port'])
        try:
            write_fun = create_ip_pair_setup_write(conn)
            pairing = perform_pair_setup(pin, str(uuid.uuid4()), write_fun)
        finally:
            conn.close()
        pairing['AccessoryIP'] = connection_data['ip']
        pairing['AccessoryPort'] = connection_data['port']
        pairing['Connection'] = 'IP'
        self.pairings[alias] = IpPairing(pairing)

    def perform_pairing_ble(self, alias, accessory_mac, pin):
        """
        This performs a pairing attempt with the Bluetooth LE accessory identified by its mac address.

        Accessories can be found via the discover method. The mac field is the accessory's mac for the second parameter.

        The required pin is either printed on the accessory or displayed. Must be a string of the form 'XXX-YY-ZZZ'.

        Important: no automatic saving of the pairing data is performed. If you don't do this, the information is lost
            and you have to reset the accessory!

        :param alias: the alias for the accessory in the controllers data
        :param accessory_mac: the accessory's mac address
        :param pin: the accessory's pin
        # TODO add raised exceptions
        """
        if alias in self.pairings:
            raise AlreadyPairedError('Alias "{a}" is already paired.'.format(a=alias))

        from .ble_impl.device import DeviceManager
        manager = DeviceManager(adapter_name='hci0')
        device = manager.make_device(mac_address=accessory_mac)

        logging.debug('connecting to device')
        device.connect()
        logging.debug('connected to device')

        pair_setup_char, pair_setup_char_id = find_characteristic_by_uuid(device, ServicesTypes.PAIRING_SERVICE,
                                                                          CharacteristicsTypes.PAIR_SETUP)
        logging.debug('setup char: %s %s', pair_setup_char, pair_setup_char.service.device)

        write_fun = create_ble_pair_setup_write(pair_setup_char, pair_setup_char_id)
        pairing = perform_pair_setup(pin, str(uuid.uuid4()), write_fun)

        pairing['AccessoryMAC'] = accessory_mac
        pairing['Connection'] = 'BLE'

        self.pairings[alias] = BlePairing(pairing)

    def remove_pairing(self, alias):
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
        # package visibility like in java would be nice here
        pairing_data = self.pairings[alias]._get_pairing_data()
        connection_type = pairing_data['Connection']

        # Prepare the common (for IP and BLE) request data
        request_tlv = TLV.encode_list([
            (TLV.kTLVType_State, TLV.M1),
            (TLV.kTLVType_Method, TLV.RemovePairing),
            (TLV.kTLVType_Identifier, pairing_data['iOSPairingId'].encode())
        ])

        if connection_type == 'IP':
            session = IpSession(pairing_data)
            # decode is required because post needs a string representation
            response = session.post('/pairings', request_tlv.decode())
            session.close()
            data = response.read()
            data = TLV.decode_bytes(data)
        elif connection_type == 'BLE':
            inner = TLV.encode_list([
                (TLV.kTLVHAPParamParamReturnResponse, bytearray(b'\x01')),
                (TLV.kTLVHAPParamValue, request_tlv)
            ])

            body = len(inner).to_bytes(length=2, byteorder='little') + inner

            from .ble_impl.device import DeviceManager
            manager = DeviceManager(adapter_name='hci0')
            device =  manager.make_device(pairing_data['AccessoryMAC'])
            device.connect()
            #
            logging.debug('resolved %d services', len(device.services))
            pair_remove_char, pair_remove_char_id = find_characteristic_by_uuid(device, ServicesTypes.PAIRING_SERVICE,
                                                                                CharacteristicsTypes.PAIRING_PAIRINGS)
            logging.debug('setup char: %s %s', pair_remove_char, pair_remove_char.service.device)

            session = BleSession(pairing_data)
            response = session.request(pair_remove_char, pair_remove_char_id, HapBleOpCodes.CHAR_WRITE, body)
            data = TLV.decode_bytes(response[1])
        else:
            raise Exception('not implemented (neither IP nor BLE)')

        # act upon the response (the same is returned for IP and BLE accessories)
        # handle the result, spec says, if it has only one entry with state == M2 we unpaired, else its an error.
        logging.debug('response data: %s', data)
        if len(data) == 1 and data[0][0] == TLV.kTLVType_State and data[0][1] == TLV.M2:
            del self.pairings[alias]
        else:
            if data[1][0] == TLV.kTLVType_Error and data[1][1] == TLV.kTLVError_Authentication:
                raise AuthenticationError('Remove pairing failed: missing authentication')
            else:
                raise UnknownError('Remove pairing failed: unknown error')
