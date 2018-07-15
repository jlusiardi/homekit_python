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

import unittest

from homekit.crypto.srp import *


class TestSrp(unittest.TestCase):

    def test_1(self):
        # step M1

        # step M2
        setup_code = '123-45-678'  # transmitted on second channel
        server = SrpServer('Pair-Setup', setup_code)
        server_pub_key = server.get_public_key()
        server_salt = server.get_salt()

        # step M3
        client = SrpClient('Pair-Setup', setup_code)
        client.set_salt(server_salt)
        client.set_server_public_key(server_pub_key)

        client_pub_key = client.get_public_key()
        clients_proof = client.get_proof()

        # step M4
        server.set_client_public_key(client_pub_key)
        server_shared_secret = server.get_shared_secret()
        self.assertTrue(server.verify_clients_proof(clients_proof))
        servers_proof = server.get_proof(clients_proof)

        # step M5
        self.assertTrue(client.verify_servers_proof(servers_proof))

