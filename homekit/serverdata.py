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
import binascii

from homekit.exception import ConfigurationException
from homekit.model import Categories


class HomeKitServerData:
    """
    This class is used to take care of the servers persistence to be able to managage restarts,
    """

    def __init__(self, data_file):
        self.data_file = data_file
        with open(data_file, 'r') as input_file:
            self.data = json.load(input_file)
        # set some default values
        if 'peers' not in self.data:
            self.data['peers'] = {}
        if 'unsuccessful_tries' not in self.data:
            self.data['unsuccessful_tries'] = 0

    def _save_data(self):
        with open(self.data_file, 'w') as output_file:
            # print(json.dumps(self.data, indent=2, sort_keys=True))
            json.dump(self.data, output_file, indent=2, sort_keys=True)

    @property
    def ip(self) -> str:
        return self.data['host_ip']

    @property
    def port(self) -> int:
        return self.data['host_port']

    @property
    def setup_code(self) -> str:
        return self.data['accessory_pin']

    @property
    def accessory_pairing_id_bytes(self) -> bytes:
        return self.data['accessory_pairing_id'].encode()

    @property
    def unsuccessful_tries(self) -> int:
        return self.data['unsuccessful_tries']

    def register_unsuccessful_try(self):
        self.data['unsuccessful_tries'] += 1
        self._save_data()

    @property
    def is_paired(self) -> bool:
        return len(self.data['peers']) > 0

    @property
    def name(self) -> str:
        return self.data['name']

    @property
    def category(self) -> str:
        try:
            category = self.data['category']
        except KeyError:
            raise ConfigurationException('category missing in "{f}"'.format(f=self.data_file))
        if category not in Categories:
            raise ConfigurationException('invalid category "{c}" in "{f}"'.format(c=category, f=self.data_file))
        return category

    def remove_peer(self, pairing_id: bytes):
        del self.data['peers'][pairing_id.decode()]
        self._save_data()

    def add_peer(self, pairing_id: bytes, ltpk: bytes, admin=True):
        self.data['peers'][pairing_id.decode()] = {'key': binascii.hexlify(ltpk).decode(), 'admin': admin}
        self._save_data()

    def get_peer_key(self, pairing_id: bytes) -> bytes:
        if pairing_id.decode() in self.data['peers']:
            return bytes.fromhex(self.data['peers'][pairing_id.decode()]['key'])
        else:
            return None

    def is_peer_admin(self, pairing_id: bytes) -> bool:
        return self.data['peers'][pairing_id.decode()]['admin']

    def set_peer_permissions(self, pairing_id: bytes, admin):
        self.data['peers'][pairing_id.decode()]['admin'] = admin

    @property
    def peers(self):
        return self.data['peers'].keys()

    @property
    def accessory_ltsk(self) -> bytes:
        if 'accessory_ltsk' in self.data:
            return bytes.fromhex(self.data['accessory_ltsk'])
        else:
            return None

    @property
    def accessory_ltpk(self) -> bytes:
        if 'accessory_ltpk' in self.data:
            return bytes.fromhex(self.data['accessory_ltpk'])
        else:
            return None

    def set_accessory_keys(self, accessory_ltpk: bytes, accessory_ltsk: bytes):
        self.data['accessory_ltpk'] = binascii.hexlify(accessory_ltpk).decode()
        self.data['accessory_ltsk'] = binascii.hexlify(accessory_ltsk).decode()
        self._save_data()

    @property
    def configuration_number(self) -> int:
        return self.data['c#']

    def increase_configuration_number(self):
        self.data['c#'] += 1
        self._save_data()

    def check(self, paired=False):
        """
        Checks a accessory config file for completeness.
        :param paired: if True, check for keys that must exist after successful pairing as well.
        :return: None, but a HomeKitConfigurationException is raised if a key is missing
        """
        required_fields = ['name', 'host_ip', 'host_port', 'accessory_pairing_id', 'accessory_pin', 'c#', 'category']
        if paired:
            required_fields.extend(['accessory_ltpk', 'accessory_ltsk', 'peers', 'unsuccessful_tries'])
        for f in required_fields:
            if f not in self.data:
                raise ConfigurationException(
                    '"{r}" is missing in the config file "{f}"!'.format(r=f, f=self.data_file))

        category = self.data['category']
        if category not in Categories:
            raise ConfigurationException('invalid category "{c}" in "{f}"'.format(c=category, f=self.data_file))
