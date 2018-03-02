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


class HomeKitServerData:
    """
    This class is used to take care of the servers persistence to be able to managage restarts,
    """

    def __init__(self, data_file):
        self.data_file = data_file
        with open(data_file, 'r') as input_file:
            self.data = json.load(input_file)

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

    def remove_peer(self, pairing_id: bytes):
        del self.data['peers'][pairing_id.decode()]
        self._save_data()

    def add_peer(self, pairing_id: bytes, ltpk: bytes):
        admin = (len(self.data['peers']) == 0)
        self.data['peers'][pairing_id.decode()] = {'key': binascii.hexlify(ltpk).decode(), 'admin': admin}
        self._save_data()

    def get_peer_key(self, pairing_id: bytes) -> bytes:
        if pairing_id.decode() in self.data['peers']:
            return bytes.fromhex(self.data['peers'][pairing_id.decode()]['key'])
        else:
            return None

    def is_peer_admin(self, pairing_id: bytes) -> bool:
        return self.data['peers'][pairing_id.decode()]['admin']

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


if __name__ == '__main__':
    import tempfile

    fp = tempfile.NamedTemporaryFile(mode='w')
    data = {
        'host_ip': '12.34.56.78',
        'port': 4711,
        'accessory_pin': '123-45-678',
        'accessory_pairing_id': '12:34:56:78:90:AB',
        'name': 'test007',
        'unsuccessful_tries': 0
    }
    json.dump(data, fp)
    fp.flush()

    print(fp.name)

    hksd = HomeKitServerData(fp.name)
    print(hksd.accessory_pairing_id_bytes)
    pk = bytes([0x12, 0x34])
    sk = bytes([0x56, 0x78])
    hksd.set_accessory_keys(pk, sk)
    assert hksd.accessory_ltpk == pk
    assert hksd.accessory_ltsk == sk
