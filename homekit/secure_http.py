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
import http.client

from homekit.chacha20poly1305 import chacha20_aead_encrypt, chacha20_aead_decrypt
from homekit.statuscodes import HttpContentTypes


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

    def __init__(self, sock, a2c_key, c2a_key):
        """
        Initializes the secure HTTP class. The required keys can be obtained with get_session_keys

        :param sock: the socket over which the communication takes place
        :param a2c_key: the key used for the communication between accessory and controller
        :param c2a_key: the key used for the communication between controller and accessory
        """
        self.sock = sock
        self.a2c_key = a2c_key
        self.c2a_key = c2a_key
        self.c2a_counter = 0
        self.a2c_counter = 0

    def get(self, target):
        data = 'GET {tgt} HTTP/1.1\n\n'.format(tgt=target)

        return self._handle_request(data)

    def put(self, target, body, content_type=HttpContentTypes.JSON):
        headers = 'Host: hap-770D90.local\n' + \
                  'Content-Type: application/hap+json\n' + \
                  'Content-Length: {len}\n'.format(len=len(body))
        data = 'PUT {tgt} HTTP/1.1\n{hdr}\n{body}'.format(tgt=target, hdr=headers, body=body)
        return self._handle_request(data)

    def post(self, target, body, content_type=HttpContentTypes.TLV):
        headers = 'Host: hap-770D90.local\n' + \
                  'Content-Type: {ct}\n'.format(ct=content_type) + \
                  'Content-Length: {len}\n'.format(len=len(body))
        data = 'POST {tgt} HTTP/1.1\n{hdr}\n{body}'.format(tgt=target, hdr=headers, body=body)

        return self._handle_request(data)

    def _handle_request(self, data):
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

    def _handle_response(self):
        result = self._read_response()

        #
        #   I expected a full http response but the first real homekit accessory (Koogeek-P1) just replies with body
        #   in chunked mode...
        #
        if result.startswith(b'HTTP/1.1'):
            r = http.client.HTTPResponse(SecureHttp.Wrapper(result))
            r.begin()
            return r
        elif result.startswith(b'EVENT/1.0'):
            result = SecureHttp._parseEvents(result)
            return result
        else:
            data = SecureHttp._parse(result)
            return self.HTTPResponseWrapper(data)

    def _read_response(self):
        # following the information from page 71 about HTTP Message splitting:
        # The blocks start with 2 byte little endian defining the length of the encrypted data (max 1024 bytes)
        # followed by 16 byte authTag
        blocks = []
        tmp = bytearray()
        exp_len = 512
        while True:
            data = self.sock.recv(exp_len)
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

            blocks.append((length, block, tag))

            # check how long next block will be
            if int.from_bytes(tmp[0:2], 'little') < 1024:
                exp_len = int.from_bytes(tmp[0:2], 'little') - len(tmp) + 18

            if length < 1024:
                break
        # now decrypt the blocks and assemble the answer to our request
        result = bytearray()
        for b in blocks:
            tmp = chacha20_aead_decrypt(b[0].to_bytes(2, byteorder='little'),
                                        self.a2c_key,
                                        self.a2c_counter.to_bytes(8, byteorder='little'),
                                        bytes([0, 0, 0, 0]), b[1] + b[2])
            if tmp is not False:
                result += tmp
            self.a2c_counter += 1
        return result

    def handle_event_response(self):
        """
        This reads the enciphered response from an accessory after registering for events.
        :return: the event data as string (not as json object)
        """
        result = self._read_response()
        if result.startswith(b'EVENT/1.0'):
            tmp = result.decode()
            tmp = tmp.split('\r\n\r\n')[1]
            return tmp
        else:
            raise IOError('The response was no EVENT/1.0 data')