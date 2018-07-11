import unittest

from homekit.srp import *

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
