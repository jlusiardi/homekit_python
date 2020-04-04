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

from functools import partial
import json
from json.decoder import JSONDecodeError
import time
import logging
import tlv8

from homekit.controller.tools import AbstractPairing, check_convert_value
from homekit.protocol.statuscodes import HapStatusCodes
from homekit.exceptions import AccessoryNotFoundError, UnknownError, UnpairedError, \
    AccessoryDisconnectedError, EncryptionError
from homekit.http_impl import HomeKitHTTPConnection, HttpContentTypes
from homekit.http_impl.secure_http import SecureHttp
from homekit.protocol import get_session_keys, create_ip_pair_verify_write
from homekit.protocol import States, Methods, Errors, TlvTypes
from homekit.model.characteristics import CharacteristicsTypes
from homekit.zeroconf_impl import find_device_ip_and_port
from homekit.model.services import ServicesTypes


# Taking iPhone requests as source of truth about the format of json payloads
# there should be no whitespace after comma (or anywhere that would be just spacing).
# Some devices (like Tado Internet Bridge) are really fussy about that, and sending
# json payload in Python's standard formatting will cause it to return error.
# I.e. sending perfectly valid json:
#   {"characteristics":[{"iid":15, "aid":2, "ev":true}]}
# will not work, while:
#   {"characteristics":[{"iid":15,"aid":2,"ev":true}]}
# is accepted.
# See https://github.com/jlusiardi/homekit_python/issues/181
_dump_json = partial(json.dumps, separators=(',', ':'))


class IpPairing(AbstractPairing):
    """
    This represents a paired HomeKit IP accessory.
    """

    def __init__(self, pairing_data):
        """
        Initialize a Pairing by using the data either loaded from file or obtained after calling
        Controller.perform_pairing().

        :param pairing_data:
        """
        self.pairing_data = pairing_data
        self.session = None

    def close(self):
        """
        Close the pairing's communications. This closes the session.
        """
        if self.session:
            self.session.close()

    def _get_pairing_data(self):
        """
        This method returns the internal pairing data. DO NOT mess around with it.

        :return: a dict containing the data
        """
        return self.pairing_data

    def list_accessories_and_characteristics(self):
        """
        This retrieves a current set of accessories and characteristics behind this pairing.

        :return: the accessory data as described in the spec on page 73 and following
        :raises AccessoryNotFoundError: if the device can not be found via zeroconf
        """
        if not self.session:
            self.session = IpSession(self.pairing_data)
        try:
            response = self.session.get('/accessories')
        except (AccessoryDisconnectedError, EncryptionError):
            self.session.close()
            self.session = None
            raise
        tmp = response.read().decode()
        accessories = json.loads(tmp)['accessories']

        for accessory in accessories:
            for service in accessory['services']:
                service['type'] = service['type'].upper()
                try:
                    service['type'] = ServicesTypes.get_uuid(service['type'])
                except KeyError:
                    pass

                for characteristic in service['characteristics']:
                    characteristic['type'] = characteristic['type'].upper()
                    try:
                        characteristic['type'] = CharacteristicsTypes.get_uuid(characteristic['type'])
                    except KeyError:
                        pass

        self.pairing_data['accessories'] = accessories
        return accessories

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
        if not self.session:
            self.session = IpSession(self.pairing_data)
        request_tlv = tlv8.encode([
            tlv8.Entry(TlvTypes.State, States.M1),
            tlv8.Entry(TlvTypes.Method, Methods.ListPairings)
        ])
        try:
            response = self.session.sec_http.post('/pairings', request_tlv)
            data = response.read()
        except (AccessoryDisconnectedError, EncryptionError):
            self.session.close()
            self.session = None
            raise
        data = tlv8.decode(data, {
            TlvTypes.State: tlv8.DataType.INTEGER,
            TlvTypes.Error: tlv8.DataType.INTEGER,
            TlvTypes.Identifier: tlv8.DataType.BYTES,
            TlvTypes.PublicKey: tlv8.DataType.BYTES,
            TlvTypes.Permissions: tlv8.DataType.BYTES
        })

        error = data.first_by_id(TlvTypes.Error)
        if not (data.first_by_id(TlvTypes.State).data == States.M2):
            raise UnknownError('unexpected data received: ' + tlv8.format_string(data))
        elif error and error.data == Errors.Authentication:
            raise UnpairedError('Must be paired')
        else:
            tmp = []
            r = {}
            for d in data[1:]:
                if d.type_id == TlvTypes.Identifier:
                    r = {}
                    tmp.append(r)
                    r['pairingId'] = d.data.decode()
                if d.type_id == TlvTypes.PublicKey:
                    r['publicKey'] = d.data.hex()
                if d.type_id == TlvTypes.Permissions:
                    controller_type = 'regular'
                    if d.data == b'\x01':
                        controller_type = 'admin'
                    r['permissions'] = int.from_bytes(d.data, byteorder='little')
                    r['controllerType'] = controller_type
            tmp.sort(key=lambda x: x['pairingId'])
            return tmp

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
        if not self.session:
            self.session = IpSession(self.pairing_data)
        url = '/characteristics?id=' + ','.join([str(x[0]) + '.' + str(x[1]) for x in characteristics])
        if include_meta:
            url += '&meta=1'
        if include_perms:
            url += '&perms=1'
        if include_type:
            url += '&type=1'
        if include_events:
            url += '&ev=1'

        try:
            response = self.session.get(url)
        except (AccessoryDisconnectedError, EncryptionError):
            self.session.close()
            self.session = None
            raise

        try:
            data = json.loads(response.read().decode())['characteristics']
        except JSONDecodeError:
            self.session.close()
            self.session = None
            raise AccessoryDisconnectedError("Session closed after receiving malformed response from device")

        tmp = {}
        for c in data:
            key = (c['aid'], c['iid'])
            del c['aid']
            del c['iid']

            if 'status' in c and c['status'] == 0:
                del c['status']
            if 'status' in c and c['status'] != 0:
                c['description'] = HapStatusCodes[c['status']]
            tmp[key] = c
        return tmp

    def get_resource(self, resource_request):
        """
        This method performs a request to read the /resource endpoint of an accessory. What it does is dependend on the
        accessory being queried. For example this could be a IP based camera to return a snapshot image (see spec R2,
        chapter 11.5 page 242).
        :param resource_request: a dict of values to be sent to the accessory as a json dump
        :return: the content of the response body as bytes
        """
        if not self.session:
            self.session = IpSession(self.pairing_data)
        url = '/resource'
        body = _dump_json(resource_request).encode()

        try:
            response = self.session.post(url, body)
            content_type = 'application/octet-stream'
            for header in response.headers:
                if header[0] == 'Content-Type':
                    content_type = header[1]
            return (content_type, response.read())
        except (AccessoryDisconnectedError, EncryptionError):
            self.session.close()
            self.session = None
            raise

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
        if not self.session:
            self.session = IpSession(self.pairing_data)
        if 'accessories' not in self.pairing_data:
            self.list_accessories_and_characteristics()
        data = []
        characteristics_set = set()
        for characteristic in characteristics:
            aid = characteristic[0]
            iid = characteristic[1]
            value = characteristic[2]
            if do_conversion:
                # evaluate proper format
                c_format = None
                for d in self.pairing_data['accessories']:
                    if 'aid' in d and d['aid'] == aid:
                        for s in d['services']:
                            for c in s['characteristics']:
                                if 'iid' in c and c['iid'] == iid:
                                    c_format = c['format']

                value = check_convert_value(value, c_format)
            characteristics_set.add('{a}.{i}'.format(a=aid, i=iid))
            data.append({'aid': aid, 'iid': iid, 'value': value})
        data = _dump_json({'characteristics': data})

        try:
            response = self.session.put('/characteristics', data)
        except (AccessoryDisconnectedError, EncryptionError):
            self.session.close()
            self.session = None
            raise

        if response.code != 204:
            data = response.read().decode()
            try:
                data = json.loads(data)['characteristics']
            except JSONDecodeError:
                self.session.close()
                self.session = None
                raise AccessoryDisconnectedError("Session closed after receiving malformed response from device")

            data = {(d['aid'], d['iid']): {'status': d['status'], 'description': HapStatusCodes[d['status']]} for d in
                    data}
            return data
        return {}

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
        if not self.session:
            self.session = IpSession(self.pairing_data)
        data = []
        characteristics_set = set()
        for characteristic in characteristics:
            aid = characteristic[0]
            iid = characteristic[1]
            characteristics_set.add('{a}.{i}'.format(a=aid, i=iid))
            data.append({'aid': aid, 'iid': iid, 'ev': True})
        data = _dump_json({'characteristics': data})

        try:
            response = self.session.put('/characteristics', data)
        except (AccessoryDisconnectedError, EncryptionError):
            self.session.close()
            self.session = None
            raise

        # handle error responses
        if response.code != 204:
            tmp = {}
            try:
                data = json.loads(response.read().decode())
            except JSONDecodeError:
                self.session.close()
                self.session = None
                raise AccessoryDisconnectedError("Session closed after receiving malformed response from device")

            for characteristic in data['characteristics']:
                status = characteristic['status']
                if status == 0:
                    continue
                aid = characteristic['aid']
                iid = characteristic['iid']
                tmp[(aid, iid)] = {'status': status, 'description': HapStatusCodes[status]}
            return tmp

        # wait for incoming events
        event_count = 0
        s = time.time()
        while (max_events == -1 or event_count < max_events) and (max_seconds == -1 or s + max_seconds >= time.time()):
            try:
                r = self.session.sec_http.handle_event_response()
                body = r.read().decode()
            except (AccessoryDisconnectedError, EncryptionError):
                self.session.close()
                self.session = None
                raise

            if len(body) > 0:
                try:
                    r = json.loads(body)
                except JSONDecodeError:
                    self.session.close()
                    self.session = None
                    raise AccessoryDisconnectedError("Session closed after receiving malformed response from device")
                tmp = []
                for c in r['characteristics']:
                    tmp.append((c['aid'], c['iid'], c['value']))
                callback_fun(tmp)
                event_count += 1
        return {}

    def identify(self):
        """
        This call can be used to trigger the identification of a paired accessory. A successful call should
        cause the accessory to perform some specific action by which it can be distinguished from the others (blink a
        LED for example).

        It uses the identify characteristic as described on page 152 of the spec.

        :return True, if the identification was run, False otherwise
        """
        if not self.session:
            self.session = IpSession(self.pairing_data)
        if 'accessories' not in self.pairing_data:
            self.list_accessories_and_characteristics()

        # we are looking for a characteristic of the identify type
        identify_type = CharacteristicsTypes.get_uuid(CharacteristicsTypes.IDENTIFY)

        # search all accessories, all services and all characteristics
        for accessory in self.pairing_data['accessories']:
            aid = accessory['aid']
            for service in accessory['services']:
                for characteristic in service['characteristics']:
                    iid = characteristic['iid']
                    c_type = CharacteristicsTypes.get_uuid(characteristic['type'])
                    if identify_type == c_type:
                        # found the identify characteristic, so let's put a value there
                        self.put_characteristics([(aid, iid, True)])
                        return True
        return False

    def add_pairing(self, additional_controller_pairing_identifier, ios_device_ltpk, permissions):
        if not self.session:
            self.session = IpSession(self.pairing_data)
        if permissions == 'User':
            permissions = TlvTypes.Permission_RegularUser
        elif permissions == 'Admin':
            permissions = TlvTypes.Permission_AdminUser
        else:
            print('UNKNOWN')

        request_tlv = tlv8.encode([
            tlv8.Entry(TlvTypes.State, States.M1),
            tlv8.Entry(TlvTypes.Method, Methods.AddPairing),
            tlv8.Entry(TlvTypes.Identifier, additional_controller_pairing_identifier.encode()),
            tlv8.Entry(TlvTypes.PublicKey, bytes.fromhex(ios_device_ltpk)),
            tlv8.Entry(TlvTypes.Permissions, permissions)
        ])

        response = self.session.sec_http.post('/pairings', request_tlv)
        data = response.read()
        data = tlv8.decode(data, {
            TlvTypes.State: tlv8.DataType.INTEGER,
            TlvTypes.Error: tlv8.DataType.BYTES,
        })
        # TODO handle the response properly
        self.session.close()


class IpSession(object):
    def __init__(self, pairing_data):
        """

        :param pairing_data:
        :raises AccessoryNotFoundError: if the device can not be found via zeroconf
        """
        logging.debug('init session')
        connected = False
        self.pairing_data = pairing_data

        if 'AccessoryIP' in pairing_data and 'AccessoryPort' in pairing_data:
            # if it is known, try it
            accessory_ip = pairing_data['AccessoryIP']
            accessory_port = pairing_data['AccessoryPort']
            connected = self._connect(accessory_ip, accessory_port)

        if not connected:
            # no connection yet, so ip / port might have changed and we need to fall back to slow zeroconf lookup
            device_id = pairing_data['AccessoryPairingID']
            connection_data = find_device_ip_and_port(device_id)

            # update pairing data with the IP/port we elaborated above, perhaps next time they are valid
            pairing_data['AccessoryIP'] = connection_data['ip']
            pairing_data['AccessoryPort'] = connection_data['port']

            if connection_data is None:
                raise AccessoryNotFoundError(
                    'Device {id} not found'.format(id=pairing_data['AccessoryPairingID']))

            if not self._connect(connection_data['ip'], connection_data['port']):
                return

        logging.debug('session established')

        self.sec_http = SecureHttp(self)

    def _connect(self, accessory_ip, accessory_port):
        conn = HomeKitHTTPConnection(accessory_ip, port=accessory_port)
        try:
            conn.connect()
            write_fun = create_ip_pair_verify_write(conn)

            state_machine = get_session_keys(self.pairing_data)

            request, expected = state_machine.send(None)
            while True:
                try:
                    response = write_fun(request, expected)
                    request, expected = state_machine.send(response)
                except StopIteration as result:
                    self.c2a_key, self.a2c_key = result.value
                    self.sock = conn.sock
                    return True
        except OSError as e:
            logging.debug("Failed to connect to accessory: %s", e.strerror)
        except Exception:
            logging.exception("Failed to connect to accessory")

        return False

    def close(self):
        """
        Close the session. This closes the socket.
        """
        try:
            self.sock.close()
        except OSError:
            # If we get an OSError its probably because the socket is already closed
            pass
        self.sock = None

    def get_from_pairing_data(self, key):
        if key not in self.pairing_data:
            return None
        return self.pairing_data[key]

    def set_in_pairing_data(self, key, value):
        self.pairing_data[key] = value

    def get(self, url):
        """
        Perform HTTP get via the encrypted session.
        :param url: The url to request
        :return: a homekit.http_impl.HttpResponse object
        """
        return self.sec_http.get(url)

    def put(self, url, body, content_type=HttpContentTypes.JSON):
        """
        Perform HTTP put via the encrypted session.
        :param url: The url to request
        :param body: the body of the put request
        :param content_type: the content of the content-type header
        :return: a homekit.http_impl.HttpResponse object
        """
        return self.sec_http.put(url, body, content_type)

    def post(self, url, body, content_type=HttpContentTypes.JSON):
        """
        Perform HTTP post via the encrypted session.
        :param url: The url to request
        :param body: the body of the post request
        :param content_type: the content of the content-type header
        :return: a homekit.http_impl.HttpResponse object
        """
        return self.sec_http.post(url, body, content_type)
