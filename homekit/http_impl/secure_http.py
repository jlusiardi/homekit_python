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

import threading
import select
import logging

from homekit.http_impl.response import HttpResponse
from homekit.crypto.chacha20poly1305 import chacha20_aead_encrypt, chacha20_aead_decrypt
from homekit.http_impl import HttpContentTypes
from homekit import exceptions


class SecureHttp:
    """
    Class to help in the handling of HTTP requests and responses that are performed following chapter 5.5 page 70ff of
    the HAP specification.
    """

    def __init__(self, session, timeout=10):
        """
        Initializes the secure HTTP class. The required keys can be obtained with get_session_keys

        :param sock: the socket over which the communication takes place
        :param a2c_key: the key used for the communication between accessory and controller
        :param c2a_key: the key used for the communication between controller and accessory
        """
        self.sock = session.sock
        self.host = session.pairing_data['AccessoryIP']
        self.port = session.pairing_data['AccessoryPort']
        self.a2c_key = session.a2c_key
        self.c2a_key = session.c2a_key
        self.c2a_counter = 0
        self.a2c_counter = 0
        self.timeout = timeout
        self.lock = threading.Lock()

    def get(self, target):
        data = 'GET {tgt} HTTP/1.1\nHost: {host}:{port}\n\n'.format(tgt=target, host=self.host, port=self.port)
        data = data.replace("\n", "\r\n")
        return self._handle_request(data.encode())

    def put(self, target, body, content_type=HttpContentTypes.JSON):
        headers = 'Host: {host}:{port}\n'.format(host=self.host, port=self.port) + \
                  'Content-Type: {ct}\n'.format(ct=content_type) + \
                  'Content-Length: {len}\n'.format(len=len(body))
        data = 'PUT {tgt} HTTP/1.1\n{hdr}\n{body}'.format(tgt=target, hdr=headers, body=body)
        data = data.replace("\n", "\r\n")
        return self._handle_request(data.encode())

    def post(self, target, body, content_type=HttpContentTypes.TLV):
        headers = 'Host: {host}:{port}\n'.format(host=self.host, port=self.port) + \
                  'Content-Type: {ct}\n'.format(ct=content_type) + \
                  'Content-Length: {len}\n'.format(len=len(body))
        data = 'POST {tgt} HTTP/1.1\n{hdr}\n'.format(tgt=target, hdr=headers)
        data = data.replace("\n", "\r\n")
        return self._handle_request(data.encode() + body)

    def _handle_request(self, data):
        logging.debug('handle request: %s', data)
        with self.lock:
            while len(data) > 0:
                # split the data to max 1024 bytes (see page 71)
                len_data = min(len(data), 1024)
                tmp_data = data[:len_data]
                data = data[len_data:]
                len_bytes = len_data.to_bytes(2, byteorder='little')
                cnt_bytes = self.c2a_counter.to_bytes(8, byteorder='little')
                self.c2a_counter += 1
                ciper_and_mac = chacha20_aead_encrypt(len_bytes, self.c2a_key, cnt_bytes, bytes([0, 0, 0, 0]),
                                                      tmp_data)

                try:
                    self.sock.send(len_bytes + ciper_and_mac[0] + ciper_and_mac[1])
                except OSError as e:
                    raise exceptions.AccessoryDisconnectedError(str(e))

            return self._read_response(self.timeout)

    def _read_response(self, timeout=10):
        # following the information from page 71 about HTTP Message splitting:
        # The blocks start with 2 byte little endian defining the length of the encrypted data (max 1024 bytes)
        # followed by 16 byte authTag
        tmp = bytearray()
        exp_len = 1024
        response = HttpResponse()
        while not response.is_read_completely():
            # make sure we read all blocks but without blocking to long. Was introduced to support chunked transfer mode
            # from https://github.com/maximkulkin/esp-homekit
            self.sock.setblocking(0)

            no_data_remaining = (len(tmp) == 0)

            # if there is no data use the long timeout so we don't miss anything, else since there is still data go on
            # much quicker.
            if no_data_remaining:
                used_timeout = timeout
            else:
                used_timeout = 0.01
            data_ready = select.select([self.sock], [], [], used_timeout)[0]

            # check if there is anything more to do
            if not data_ready and no_data_remaining:
                break

            self.sock.settimeout(0.1)

            if len(tmp) == 0:
                data = self.sock.recv(2)
                tmp += data
                continue

            exp_len = int.from_bytes(tmp[0:2], 'little') - len(tmp) + 18
            data = self.sock.recv(exp_len)

            # ready but no data => continue
            if not data and no_data_remaining:
                continue

            tmp += data
            length = int.from_bytes(tmp[0:2], 'little')
            if length + 18 > len(tmp):
                # if the the amount of data in tmp is not length + 2 bytes for length + 16 bytes for the tag, the block
                # is not complete yet
                continue
            tmp = tmp[2:]

            block = tmp[0:length]
            tmp = tmp[length:]

            tag = tmp[0:16]
            tmp = tmp[16:]

            decrypted = self.decrypt_block(length, block, tag)
            if decrypted is not False:
                response.parse(decrypted)
            else:
                try:
                    self.sock.close()
                except OSError:
                    pass
                raise exceptions.EncryptionError('Error during transmission.')

        return response

    def decrypt_block(self, length, block, tag):
        tmp = chacha20_aead_decrypt(length.to_bytes(2, byteorder='little'),
                                    self.a2c_key,
                                    self.a2c_counter.to_bytes(8, byteorder='little'),
                                    bytes([0, 0, 0, 0]), block + tag)
        if tmp is not False:
            self.a2c_counter += 1

        return tmp

    def handle_event_response(self):
        """
        This reads the enciphered response from an accessory after registering for events.
        :return: the event data as string (not as json object)
        """
        try:
            return self._read_response(1)
        except OSError as e:
            raise exceptions.AccessoryDisconnectedError(str(e))
