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

import asyncio
import logging

from homekit.controller.tools import check_convert_value
from homekit.protocol.statuscodes import HapStatusCodes
from homekit.exceptions import AccessoryDisconnectedError, AuthenticationError, UnknownError, UnpairedError
from homekit.protocol import error_handler
from homekit.protocol.tlv import TLV
from homekit.model.characteristics import CharacteristicsTypes
from homekit.model.services import ServicesTypes

from homekit.aio.controller.pairing import AbstractPairing

from .connection import SecureHomeKitConnection


logger = logging.getLogger(__name__)


def format_characteristic_list(data):
    tmp = {}
    for c in data['characteristics']:
        key = (c['aid'], c['iid'])
        del c['aid']
        del c['iid']

        if 'status' in c and c['status'] == 0:
            del c['status']
        if 'status' in c and c['status'] != 0:
            c['description'] = HapStatusCodes[c['status']]
        tmp[key] = c
    return tmp


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
        self.connection = None
        self.connect_lock = asyncio.Lock()
        self.subscriptions = set()

        self.listeners = set()

    def event_received(self, event):
        event = format_characteristic_list(event)

        for listener in self.listeners:
            try:
                listener(event)
            except Exception:
                logger.exception("Unhandled error when processing event")

    async def connection_made(self, secure):
        if not secure:
            return

        if self.subscriptions:
            await self.subscribe(self.subscriptions)

    async def _ensure_connected(self):
        if not self.connection:
            async with self.connect_lock:
                if not self.connection:
                    self.connection = await SecureHomeKitConnection.connect(self, self.pairing_data)

        await self.connection.when_connected

    async def close(self):
        """
        Close the pairing's communications. This closes the session.
        """
        if self.connection:
            self.connection.close()
            self.connection = None

        await asyncio.sleep(0)

    async def list_accessories_and_characteristics(self):
        """
        This retrieves a current set of accessories and characteristics behind this pairing.

        :return: the accessory data as described in the spec on page 73 and following
        :raises AccessoryNotFoundError: if the device can not be found via zeroconf
        """
        await self._ensure_connected()

        response = await self.connection.get_json('/accessories')

        accessories = response['accessories']

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

    async def list_pairings(self):
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
        await self._ensure_connected()

        data = await self.connection.post_tlv('/pairings', [
            (TLV.kTLVType_State, TLV.M1),
            (TLV.kTLVType_Method, TLV.ListPairings)
        ])

        if not (data[0][0] == TLV.kTLVType_State and data[0][1] == TLV.M2):
            raise UnknownError('unexpected data received: ' + str(data))
        elif data[1][0] == TLV.kTLVType_Error and data[1][1] == TLV.kTLVError_Authentication:
            raise UnpairedError('Must be paired')
        else:
            tmp = []
            r = {}
            for d in data[1:]:
                if d[0] == TLV.kTLVType_Identifier:
                    r = {}
                    tmp.append(r)
                    r['pairingId'] = d[1].decode()
                if d[0] == TLV.kTLVType_PublicKey:
                    r['publicKey'] = d[1].hex()
                if d[0] == TLV.kTLVType_Permissions:
                    controller_type = 'regular'
                    if d[1] == b'\x01':
                        controller_type = 'admin'
                    r['permissions'] = int.from_bytes(d[1], byteorder='little')
                    r['controllerType'] = controller_type
            return tmp

    async def get_characteristics(self, characteristics, include_meta=False, include_perms=False, include_type=False,
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
        await self._ensure_connected()

        if 'accessories' not in self.pairing_data:
            await self.list_accessories_and_characteristics()

        url = '/characteristics?id=' + ','.join([str(x[0]) + '.' + str(x[1]) for x in characteristics])
        if include_meta:
            url += '&meta=1'
        if include_perms:
            url += '&perms=1'
        if include_type:
            url += '&type=1'
        if include_events:
            url += '&ev=1'

        response = await self.connection.get_json(url)

        return format_characteristic_list(response)

    async def put_characteristics(self, characteristics, do_conversion=False):
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
        await self._ensure_connected()

        if 'accessories' not in self.pairing_data:
            await self.list_accessories_and_characteristics()

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
        data = {'characteristics': data}

        response = await self.connection.put_json('/characteristics', data)
        if response:
            data = {(d['aid'], d['iid']): {'status': d['status'], 'description': HapStatusCodes[d['status']]} for d in
                    response}
            return data

        return {}

    async def subscribe(self, characteristics):
        await self._ensure_connected()
        self.subscriptions.update(set(characteristics))

        data = []
        for (aid, iid) in characteristics:
            data.append({
                'aid': aid,
                'iid': iid,
                'ev': True,
            })

        data = {'characteristics': data}

        tmp = {}

        try:
            response = await self.connection.put_json('/characteristics', data)
        except AccessoryDisconnectedError:
            return {}

        if response:
            for row in response.get('characteristics', []):
                id_tuple = (row['aid'], row['iid'])
                tmp[id_tuple] = {
                    'status': row['status'],
                    'description': HapStatusCodes[row['status']],
                }

        return tmp

    async def unsubscribe(self, characteristics):
        await self._ensure_connected()

        data = []
        for (aid, iid) in characteristics:
            data.append({
                'aid': aid,
                'iid': iid,
                'ev': False,
            })

        data = {'characteristics': data}

        response = await self.connection.put_json('/characteristics', data)

        char_set = set(characteristics)
        tmp = {}

        if response:
            for row in response:
                id_tuple = (row['aid'], row['iid'])
                tmp[id_tuple] = {
                    'status': row['status'],
                    'description': HapStatusCodes[row['status']],
                }
                char_set.discard(id_tuple)

        self.subscriptions.difference_update(char_set)

        return tmp

    def dispatcher_connect(self, callback):
        """
        Register an event handler to be called when a characteristic (or multiple characteristics) change.

        This function returns immediately. It returns a callable you can use to cancel the subscription.

        The callback is called in the event loop, but should not be a coroutine.
        """

        self.listeners.add(callback)

        def stop_listening():
            self.listeners.discard(callback)

        return stop_listening

    async def identify(self):
        """
        This call can be used to trigger the identification of a paired accessory. A successful call should
        cause the accessory to perform some specific action by which it can be distinguished from the others (blink a
        LED for example).

        It uses the identify characteristic as described on page 152 of the spec.

        :return True, if the identification was run, False otherwise
        """
        await self._ensure_connected()

        if 'accessories' not in self.pairing_data:
            await self.list_accessories_and_characteristics()

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
                        if not await self.put_characteristics([(aid, iid, True)]):
                            return True
        return False

    async def add_pairing(self, additional_controller_pairing_identifier, ios_device_ltpk, permissions):
        await self._ensure_connected()

        if permissions == 'User':
            permissions = TLV.kTLVType_Permission_RegularUser
        elif permissions == 'Admin':
            permissions = TLV.kTLVType_Permission_AdminUser
        else:
            raise RuntimeError("Unknown permission: {p}".format(p=permissions))

        request_tlv = [
            (TLV.kTLVType_State, TLV.M1),
            (TLV.kTLVType_Method, TLV.AddPairing),
            (TLV.kTLVType_Identifier, additional_controller_pairing_identifier.encode()),
            (TLV.kTLVType_PublicKey, bytes.fromhex(ios_device_ltpk)),
            (TLV.kTLVType_Permissions, permissions)
        ]

        data = await self.connection.post_tlv('/pairings', request_tlv)

        if len(data) == 1 and data[0][1] == TLV.M2:
            return True

        # Map TLV error codes to an exception
        error_handler(data[0][1], data[1][0])

    async def remove_pairing(self, pairingId):
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
        await self._ensure_connected()

        request_tlv = [
            (TLV.kTLVType_State, TLV.M1),
            (TLV.kTLVType_Method, TLV.RemovePairing),
            (TLV.kTLVType_Identifier, pairingId.encode('utf-8'))
        ]

        data = await self.connection.post_tlv('/pairings', request_tlv)

        # act upon the response (the same is returned for IP and BLE accessories)
        # handle the result, spec says, if it has only one entry with state == M2 we unpaired, else its an error.
        logging.debug('response data: %s', data)

        if len(data) == 1 and data[0][0] == TLV.kTLVType_State and data[0][1] == TLV.M2:
            return True

        self.transport.close()

        if data[1][0] == TLV.kTLVType_Error and data[1][1] == TLV.kTLVError_Authentication:
            raise AuthenticationError('Remove pairing failed: missing authentication')

        raise UnknownError('Remove pairing failed: unknown error')
