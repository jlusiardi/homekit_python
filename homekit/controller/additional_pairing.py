#
# Copyright 2019 Joachim Lusiardi
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

from homekit.controller.tools import AbstractPairing


class AdditionalPairing(AbstractPairing):
    """
    This represents an preparation state for an additional pairing (see channel chapter 4.11 Add Pairing page 51).
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
        pass

    def _get_pairing_data(self):
        """
        This method returns the internal pairing data. DO NOT mess around with it.

        :return: a dict containing the data
        """
        return self.pairing_data

    def list_accessories_and_characteristics(self):
        pass

    def list_pairings(self):
        pass

    def get_characteristics(self, characteristics, include_meta=False, include_perms=False, include_type=False,
                            include_events=False):
        pass

    def put_characteristics(self, characteristics, do_conversion=False):
        pass

    def get_events(self, characteristics, callback_fun, max_events=-1, max_seconds=-1):
        pass

    def identify(self):
        pass

    def add_pairing(self, additional_controller_pairing_identifier, ios_device_ltpk, permissions):
        pass
