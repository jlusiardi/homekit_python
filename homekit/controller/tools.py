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

import abc
import base64
import binascii
from distutils.util import strtobool

from homekit.protocol.tlv import TLV, TlvParseException
from homekit.exceptions import FormatError
from homekit.model.characteristics import CharacteristicFormats


class AbstractPairing(abc.ABC):

    def _get_pairing_data(self):
        """
        This method returns the internal pairing data. DO NOT mess around with it.

        :return: a dict containing the data
        """
        return self.pairing_data

    @abc.abstractmethod
    def close(self):
        """
        Close the pairing's communications. This closes the session.
        """
        pass

    @abc.abstractmethod
    def list_accessories_and_characteristics(self):
        """
        This retrieves a current set of accessories and characteristics behind this pairing.

        :return: the accessory data as described in the spec on page 73 and following
        :raises AccessoryNotFoundError: if the device can not be found via zeroconf
        """
        pass

    @abc.abstractmethod
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
        pass

    @abc.abstractmethod
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
        pass

    @abc.abstractmethod
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
        pass

    @abc.abstractmethod
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
        pass

    @abc.abstractmethod
    def identify(self):
        """
        This call can be used to trigger the identification of a paired accessory. A successful call should
        cause the accessory to perform some specific action by which it can be distinguished from the others (blink a
        LED for example).

        It uses the identify characteristic as described on page 152 of the spec.

        :return True, if the identification was run, False otherwise
        """
        pass

    @abc.abstractmethod
    def add_pairing(self, additional_controller_pairing_identifier, ios_device_ltpk, permissions):
        pass


def check_convert_value(val, target_type):
    """
    Checks if the given value is of the given type or is convertible into the type. If the value is not convertible, a
    HomeKitTypeException is thrown.

    :param val: the original value
    :param target_type: the target type of the conversion
    :return: the converted value
    :raises FormatError: if the input value could not be converted to the target type
    """
    if target_type == CharacteristicFormats.bool:
        try:
            val = strtobool(str(val))
        except ValueError:
            raise FormatError('"{v}" is no valid "{t}"!'.format(v=val, t=target_type))
    if target_type in [CharacteristicFormats.uint64, CharacteristicFormats.uint32,
                       CharacteristicFormats.uint16, CharacteristicFormats.uint8,
                       CharacteristicFormats.int]:
        try:
            val = int(val)
        except ValueError:
            raise FormatError('"{v}" is no valid "{t}"!'.format(v=val, t=target_type))
    if target_type == CharacteristicFormats.float:
        try:
            val = float(val)
        except ValueError:
            raise FormatError('"{v}" is no valid "{t}"!'.format(v=val, t=target_type))
    if target_type == CharacteristicFormats.data:
        try:
            base64.decodebytes(val.encode())
        except binascii.Error:
            raise FormatError('"{v}" is no valid "{t}"!'.format(v=val, t=target_type))
    if target_type == CharacteristicFormats.tlv8:
        try:
            tmp_bytes = base64.decodebytes(val.encode())
            TLV.decode_bytes(tmp_bytes)
        except (binascii.Error, TlvParseException):
            raise FormatError('"{v}" is no valid "{t}"!'.format(v=val, t=target_type))
    return val
