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
from unittest import mock
import socket
import threading

from homekit.http_impl.secure_http import SecureHttp
from homekit.exceptions import AccessoryDisconnectedError, EncryptionError
from homekit.crypto.chacha20poly1305 import chacha20_aead_encrypt, chacha20_aead_decrypt

class ResponseProvider(threading.Thread):
    """

    """

    data = ['HTTP/1.1 200 OK\r\nContent-Length: 0\r\n\r\n']

    def __init__(self, sock, c2a_key, a2c_key, encryption_fail=False):
        threading.Thread.__init__(self)
        self.sock = sock
        self.c2a_key = c2a_key
        self.a2c_key = a2c_key
        self.a2c_counter = 0
        self.c2a_counter = 0
        self.encryption_fail = encryption_fail

    def run(self):
        tmp = self.sock.recv(1024)
        length = int.from_bytes(tmp[0:2], 'little')
        tmp = tmp[2:]
        block = tmp[0:length]
        tmp = tmp[length:]
        tag = tmp[0:16]
        request = chacha20_aead_decrypt(length.to_bytes(2, byteorder='little'),
                                        self.c2a_key,
                                        self.c2a_counter.to_bytes(8, byteorder='little'),
                                        bytes([0, 0, 0, 0]), block + tag)

        assert b'Host:' in request

        self.c2a_counter += 1

        combined_data = b''
        for data in self.data:
            len_bytes = len(data).to_bytes(2, byteorder='little')
            cnt_bytes = self.a2c_counter.to_bytes(8, byteorder='little')
            self.a2c_counter += 1
            ciper_and_mac = chacha20_aead_encrypt(len_bytes, self.a2c_key, cnt_bytes, bytes([0, 0, 0, 0]),
                                                data.encode())

            if self.encryption_fail:
                ciper_and_mac[0][0] = 0

            combined_data += len_bytes + ciper_and_mac[0] + ciper_and_mac[1]

        self.sock.send(combined_data)


class TestSecureHttp(unittest.TestCase):
    def test_get_on_disconnected_device(self):
        with mock.patch('homekit.controller.ip_implementation.IpSession') as session:
            session.sock = socket.socket()
            session.a2c_key = b'\x00' * 32
            session.c2a_key = b'\x00' * 32
            session.pairing_data = {
                'AccessoryIP': '10.0.0.2',
                'AccessoryPort': 3000,
            }

            sh = SecureHttp(session)
            self.assertRaises(AccessoryDisconnectedError, sh.get, '/')

    def test_put_on_disconnected_device(self):
        with mock.patch('homekit.controller.ip_implementation.IpSession') as session:
            session.sock = socket.socket()
            session.a2c_key = b'\x00' * 32
            session.c2a_key = b'\x00' * 32
            session.pairing_data = {
                'AccessoryIP': '10.0.0.2',
                'AccessoryPort': 3000,
            }

            sh = SecureHttp(session)
            self.assertRaises(AccessoryDisconnectedError, sh.put, '/', 'data')

    def test_post_on_disconnected_device(self):
        with mock.patch('homekit.controller.ip_implementation.IpSession') as session:
            session.sock = socket.socket()
            session.a2c_key = b'\x00' * 32
            session.c2a_key = b'\x00' * 32
            session.pairing_data = {
                'AccessoryIP': '10.0.0.2',
                'AccessoryPort': 3000,
            }

            sh = SecureHttp(session)
            self.assertRaises(AccessoryDisconnectedError, sh.post, '/', 'data')

    def test_get_on_connected_device_timeout(self):
        with mock.patch('homekit.controller.ip_implementation.IpSession') as session:
            controller_socket, accessory_socket = socket.socketpair()

            session.sock = controller_socket

            session.a2c_key = b'\x00' * 32
            session.c2a_key = b'\x00' * 32
            session.pairing_data = {
                'AccessoryIP': '10.0.0.2',
                'AccessoryPort': 3000,
            }

            sh = SecureHttp(session, timeout=1)
            result = sh.get('/')
            controller_socket.close()
            accessory_socket.close()
            self.assertIsNone(result.code)

    def test_get_on_connected_device(self):
        controller_socket, accessory_socket = socket.socketpair()

        key_c2a = b'S2}\xb1}-l\n\x83\xe5}\'U\xc0\x1b\x0f\x08%X\xfdu\x1f\x9el/\x9bZ"\xec5\xa5P'
        key_a2c = b'\x16\xab\xd3\xfe\x95{\xe56\x1fH\x81\xfd\x914\xa0@\xaa\x0e\xa6\xebw\xf2\xe3w:\x11/\x01\xbb;,\x1d'

        tthread = ResponseProvider(accessory_socket, key_c2a, key_a2c)
        tthread.start()

        with mock.patch('homekit.controller.ip_implementation.IpSession') as session:
            session.sock = controller_socket
            session.a2c_key = key_a2c
            session.c2a_key = key_c2a
            session.pairing_data = {
                'AccessoryIP': '10.0.0.2',
                'AccessoryPort': 3000,
            }

            sh = SecureHttp(session, timeout=10)
            result = sh.get('/')

        controller_socket.close()
        accessory_socket.close()
        self.assertEqual(200, result.code)
        self.assertEqual(b'', result.body)

    def test_get_on_connected_device_enc_fail(self):
        controller_socket, accessory_socket = socket.socketpair()

        key_c2a = b'S2}\xb1}-l\n\x83\xe5}\'U\xc0\x1b\x0f\x08%X\xfdu\x1f\x9el/\x9bZ"\xec5\xa5P'
        key_a2c = b'\x16\xab\xd3\xfe\x95{\xe56\x1fH\x81\xfd\x914\xa0@\xaa\x0e\xa6\xebw\xf2\xe3w:\x11/\x01\xbb;,\x1d'

        tthread = ResponseProvider(accessory_socket, key_c2a, key_a2c, encryption_fail=True)
        tthread.start()

        with mock.patch('homekit.controller.ip_implementation.IpSession') as session:
            session.sock = controller_socket
            session.a2c_key = key_a2c
            session.c2a_key = key_c2a
            session.pairing_data = {
                'AccessoryIP': '10.0.0.2',
                'AccessoryPort': 3000,
            }

            sh = SecureHttp(session, timeout=10)
            self.assertRaises(EncryptionError, sh.get, '/')

        controller_socket.close()
        accessory_socket.close()

    def test_negative_expected_length(self):
        # Regression test - in some versions of the secure http code 3 blocks of different lengths
        # could together trigger an attempt to read negative bytes from the socket.
        controller_socket, accessory_socket = socket.socketpair()

        key_c2a = b'S2}\xb1}-l\n\x83\xe5}\'U\xc0\x1b\x0f\x08%X\xfdu\x1f\x9el/\x9bZ"\xec5\xa5P'
        key_a2c = b'\x16\xab\xd3\xfe\x95{\xe56\x1fH\x81\xfd\x914\xa0@\xaa\x0e\xa6\xebw\xf2\xe3w:\x11/\x01\xbb;,\x1d'

        tthread = ResponseProvider(accessory_socket, key_c2a, key_a2c)
        tthread.data = ['HTTP/1.1 200 OK\r\nContent-Length: 1025\r\n\r\n', ' ' * 946, ' ' * 79]
        tthread.start()

        with mock.patch('homekit.controller.ip_implementation.IpSession') as session:
            session.sock = controller_socket
            session.a2c_key = key_a2c
            session.c2a_key = key_c2a
            session.pairing_data = {
                'AccessoryIP': '10.0.0.2',
                'AccessoryPort': 3000,
            }

            sh = SecureHttp(session, timeout=10)
            result = sh.get('/')

        controller_socket.close()
        accessory_socket.close()
        self.assertEqual(200, result.code)
        self.assertEqual(bytearray(b' ' * 1025), result.body)
