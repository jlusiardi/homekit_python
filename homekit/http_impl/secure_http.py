# -*- coding: UTF-8 -*-

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

import io
import select
import threading
import http.client

from homekit.crypto.chacha20poly1305 import chacha20_aead_encrypt, chacha20_aead_decrypt
from homekit.http_impl import HttpContentTypes
from homekit.http_impl import HttpResponse


class SecureHttp:
    """
    Class to helf in the handling of HTTP requests and responses that are performed following chapter 5.5 page 70ff of
    the HAP specification.
    """

    class Wrapper:
        def __init__(self, data):
            self.data = data

        def makefile(self, arg):
            return io.BytesIO(self.data)

    class HTTPResponseWrapper:
        def __init__(self, data):
            self.data = data
            self.status = 200

        def read(self):
            return self.data

    def __init__(self, session):
        """
        Initializes the secure HTTP class. The required keys can be obtained with get_session_keys

        :param sock: the socket over which the communication takes place
        :param a2c_key: the key used for the communication between accessory and controller
        :param c2a_key: the key used for the communication between controller and accessory
        """
        self.sock = session.sock
        self.a2c_key = session.a2c_key
        self.c2a_key = session.c2a_key
        self.c2a_counter = 0
        self.a2c_counter = 0
        self.lock = threading.Lock()

    def get(self, target):
        data = 'GET {tgt} HTTP/1.1\n\n'.format(tgt=target)

        return self._handle_request(data)

    def put(self, target, body, content_type=HttpContentTypes.JSON):
        headers = 'Content-Type: {ct}\n'.format(ct=content_type) + \
                  'Content-Length: {len}\n'.format(len=len(body))
        data = 'PUT {tgt} HTTP/1.1\n{hdr}\n{body}'.format(tgt=target, hdr=headers, body=body)
        return self._handle_request(data)

    def post(self, target, body, content_type=HttpContentTypes.TLV):
        headers = 'Content-Type: {ct}\n'.format(ct=content_type) + \
                  'Content-Length: {len}\n'.format(len=len(body))
        data = 'POST {tgt} HTTP/1.1\n{hdr}\n{body}'.format(tgt=target, hdr=headers, body=body)
        return self._handle_request(data)

    def _handle_request(self, data):
        with self.lock:
            data = data.replace("\n", "\r\n")
            assert len(data) < 1024
            len_bytes = len(data).to_bytes(2, byteorder='little')
            cnt_bytes = self.c2a_counter.to_bytes(8, byteorder='little')
            self.c2a_counter += 1
            ciper_and_mac = chacha20_aead_encrypt(len_bytes, self.c2a_key, cnt_bytes, bytes([0, 0, 0, 0]), data.encode())
            self.sock.send(len_bytes + ciper_and_mac[0] + ciper_and_mac[1])
            return self._handle_response()

    @staticmethod
    def _parse(chunked_data):
        splitter = b'\r\n'
        tmp = chunked_data.split(splitter, 1)
        length = int(tmp[0].decode(), 16)
        if length == 0:
            return bytearray()

        chunk = tmp[1][:length]
        tmp[1] = tmp[1][length + 2:]
        return chunk + SecureHttp._parse(tmp[1])

    def _read_response(self, timeout=10):
        # following the information from page 71 about HTTP Message splitting:
        # The blocks start with 2 byte little endian defining the length of the encrypted data (max 1024 bytes)
        # followed by 16 byte authTag
        blocks = []
        tmp = bytearray()
        exp_len = 1024
        response = HttpResponse()
        while not response.is_read_completly():
            # make sure we read all blocks but without blocking to long. Was introduced to support chunked transfer mode
            # from https://github.com/maximkulkin/esp-homekit
            self.sock.setblocking(0)
            ready = select.select([self.sock], [], [], timeout)
            if not ready[0]:
                #break
                # TODO we disrespect the timeout here at the moment
                continue

            self.sock.settimeout(0.1)
            data = self.sock.recv(exp_len)

            # ready but no data => quit
            if not data:
                break

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

            decypted = self.decrypt_block(length, block, tag)
            # TODO how to react to False?
            if tmp is not False:
                response.parse(decypted)

            # check how long next block will be
            if int.from_bytes(tmp[0:2], 'little') < 1024:
                exp_len = int.from_bytes(tmp[0:2], 'little') - len(tmp) + 18

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
        # Must be 2 for the esp-homekits, they seem slow
        return self._read_response(1)
