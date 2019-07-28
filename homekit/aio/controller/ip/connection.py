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

import asyncio
import json
import logging

from homekit.crypto.chacha20poly1305 import chacha20_aead_encrypt, chacha20_aead_decrypt
from homekit.exceptions import AccessoryDisconnectedError
from homekit.http_impl import HttpContentTypes
from homekit.http_impl.response import HttpResponse
from homekit.protocol import get_session_keys
from homekit.protocol.tlv import TLV


logger = logging.getLogger(__name__)


class InsecureHomeKitProtocol(asyncio.Protocol):

    def __init__(self, connection):
        self.connection = connection
        self.host = ':'.join((connection.host, str(connection.port)))
        self.result_cbs = []
        self.current_response = HttpResponse()

    def connection_made(self, transport):
        super().connection_made(transport)
        self.transport = transport

    def connection_lost(self, exception):
        self.connection._connection_lost(exception)

    async def send_bytes(self, payload):
        if self.transport.is_closing():
            # FIXME: It would be nice to try and wait for the reconnect in future.
            # In that case we need to make sure we do it at a layer above send_bytes otherwise
            # we might encrypt payloads with the last sessions keys then wait for a new connection
            # to send them - and on that connection the keys would be different.
            # Also need to make sure that the new connection has chance to pair-verify before
            # queued writes can happy.
            raise AccessoryDisconnectedError('Transport is closed')

        self.transport.write(payload)

        # We return a future so that our caller can block on a reply
        # We can send many requests and dispatch the results in order
        # Should mean we don't need locking around request/reply cycles
        result = asyncio.Future()
        self.result_cbs.append(result)

        try:
            return await asyncio.wait_for(result, 10)
        except asyncio.TimeoutError:
            self.transport.write_eof()
            self.transport.close()
            raise AccessoryDisconnectedError("Timeout while waiting for response")

    def data_received(self, data):
        while data:
            data = self.current_response.parse(data)

            if self.current_response.is_read_completely():
                http_name = self.current_response.get_http_name().lower()
                if http_name == 'http':
                    next_callback = self.result_cbs.pop(0)
                    next_callback.set_result(self.current_response)
                elif http_name == 'event':
                    self.connection.event_received(self.current_response)
                else:
                    raise RuntimeError('Unknown http type')

                self.current_response = HttpResponse()

    def eof_received(self):
        self.close()
        return False

    def close(self):
        # If the connection is closed then any pending callbacks will never
        # fire, so set them to an error state.
        while self.result_cbs:
            result = self.result_cbs.pop(0)
            result.set_exception(AccessoryDisconnectedError('Connection closed'))


class SecureHomeKitProtocol(InsecureHomeKitProtocol):

    def __init__(self, connection, a2c_key, c2a_key):
        super().__init__(connection)

        self._incoming_buffer = bytearray()

        self.c2a_counter = 0
        self.a2c_counter = 0

        self.a2c_key = a2c_key
        self.c2a_key = c2a_key

    async def send_bytes(self, payload):
        buffer = b''

        while len(payload) > 0:
            current = payload[:1024]
            payload = payload[1024:]

            len_bytes = len(current).to_bytes(2, byteorder='little')
            cnt_bytes = self.c2a_counter.to_bytes(8, byteorder='little')
            self.c2a_counter += 1

            data, tag = chacha20_aead_encrypt(
                len_bytes,
                self.c2a_key,
                cnt_bytes,
                bytes([0, 0, 0, 0]),
                current,
            )

            buffer += len_bytes + data + tag

        return await super().send_bytes(buffer)

    def data_received(self, data):
        """
        Called by asyncio when data is received from a TCP socket.

        This just handles decryption of 1024 blocks and its them over to the underlying
        InsecureHomeKitProtocol to handle HTTP unframing.

        The blocks are expected to be in order - there is no protocol level support for
        interleaving of HTTP messages.
        """

        self._incoming_buffer += data

        while len(self._incoming_buffer) >= 2:
            block_length_bytes = self._incoming_buffer[:2]
            block_length = int.from_bytes(block_length_bytes, 'little')
            exp_length = block_length + 18

            if len(self._incoming_buffer) < exp_length:
                # Not enough data yet
                return

            # Drop the length from the top of the buffer as we have already parsed it
            del self._incoming_buffer[:2]

            block = self._incoming_buffer[:block_length]
            del self._incoming_buffer[:block_length]
            tag = self._incoming_buffer[:16]
            del self._incoming_buffer[:16]

            decrypted = chacha20_aead_decrypt(
                block_length_bytes,
                self.a2c_key,
                self.a2c_counter.to_bytes(8, byteorder='little'),
                bytes([0, 0, 0, 0]),
                block + tag
            )

            if decrypted is False:
                # FIXME: Does raising here drop the connection or do we call close on transport ourselves
                raise RuntimeError('Could not decrypt block')

            self.a2c_counter += 1

            super().data_received(decrypted)


class HomeKitConnection:

    def __init__(self, owner, host, port, auto_reconnect=True):
        self.owner = owner
        self.host = host
        self.port = port
        self.auto_reconnect = auto_reconnect

        self.when_connected = asyncio.Future()
        self.closing = False
        self.closed = False
        self._retry_interval = 0.5

        self.transport = None
        self.protocol = None

        # FIXME: Assume auto-reconnecting? If you are using the asyncio its probably because
        # you are running some kind of long running service, so none auto-reconnecting doesnt make
        # sense

    @classmethod
    async def connect(cls, *args, **kwargs):
        connection = cls(*args, **kwargs)

        if connection.auto_reconnect:
            await connection._reconnect()
        else:
            await connection._connect_once()

        return connection

    async def get(self, target):
        """
        Sends a HTTP POST request to the current transport and returns an awaitable
        that can be used to wait for a response.
        """
        return await self.request(
            method='GET',
            target=target,
        )

    async def get_json(self, target):
        response = await self.get(target)
        body = response.body.decode('utf-8')
        return json.loads(body)

    async def put(self, target, body, content_type=HttpContentTypes.JSON):
        """
        Sends a HTTP POST request to the current transport and returns an awaitable
        that can be used to wait for a response.
        """
        return await self.request(
            method='PUT',
            target=target,
            headers=[
                ('Content-Type', content_type),
                ('Content-Length', len(body)),
            ],
            body=body,
        )

    async def put_json(self, target, body):
        response = await self.put(
            target,
            json.dumps(body).encode('utf-8'),
            content_type=HttpContentTypes.TLV,
        )

        if response.code != 204:
            # FIXME: ...
            pass

        decoded = response.body.decode('utf-8')

        if not decoded:
            # FIXME: Verify this is correct
            return {}

        try:
            parsed = json.loads(decoded)
        except json.JSONDecodeError:
            self.transport.close()
            raise AccessoryDisconnectedError("Session closed after receiving malformed response from device")

        return parsed

    async def post(self, target, body, content_type=HttpContentTypes.TLV):
        """
        Sends a HTTP POST request to the current transport and returns an awaitable
        that can be used to wait for a response.
        """
        return await self.request(
            method='POST',
            target=target,
            headers=[
                ('Content-Type', content_type),
                ('Content-Length', len(body)),
            ],
            body=body,
        )

    async def post_json(self, target, body):
        response = await self.post(
            target,
            json.dumps(body).encode('utf-8'),
            content_type=HttpContentTypes.TLV,
        )

        if response.code != 204:
            # FIXME: ...
            pass

        decoded = response.body.decode('utf-8')

        if not decoded:
            # FIXME: Verify this is correct
            return {}

        try:
            parsed = json.loads(decoded)
        except json.JSONDecodeError:
            self.transport.close()
            raise AccessoryDisconnectedError("Session closed after receiving malformed response from device")

        return parsed

    async def post_tlv(self, target, body, expected=None):
        response = await self.post(
            target,
            TLV.encode_list(body),
            content_type=HttpContentTypes.TLV,
        )
        body = TLV.decode_bytes(response.body, expected=expected)
        return body

    async def request(self, method, target, headers=None, body=None):
        """
        Sends a HTTP request to the current transport and returns an awaitable
        that can be used to wait for the response.

        This will automatically set the header.

        :param method: A HTTP method, like 'GET' or 'POST'
        :param target: A URI to call the method on
        :param headers: a list of (header, value) tuples (optional)
        :param body: The body of the request (optional)
        """
        buffer = []
        buffer.append('{method} {target} HTTP/1.1'.format(
            method=method.upper(),
            target=target,
        ))

        # WARNING: It is vital that a Host: header is present or some devices
        # will reject the request.
        buffer.append('Host: {host}'.format(host=self.host))

        if headers:
            for (header, value) in headers:
                buffer.append('{header}: {value}'.format(
                    header=header,
                    value=value
                ))

        buffer.append('')
        buffer.append('')

        # WARNING: We use \r\n explicitly. \n is not enough for some.
        request_bytes = '\r\n'.join(buffer).encode('utf-8')

        if body:
            request_bytes += body

        # WARNING: It is vital that each request is sent in one call
        # Some devices are sensitive to unecrypted HTTP requests made in
        # multiple packets.

        # https://github.com/jlusiardi/homekit_python/issues/12
        # https://github.com/jlusiardi/homekit_python/issues/16

        return await self.protocol.send_bytes(request_bytes)

    @property
    def is_secure(self):
        if not self.protocol:
            return False
        return isinstance(self.protocol, SecureHomeKitProtocol)

    def close(self):
        """
        Close the connection transport.
        """
        self.closing = True

        if self.transport:
            self.transport.close()

    def _connection_lost(self, exception):
        """
        Called by a Protocol instance when eof_received happens.
        """
        logger.info("Connection %r lost.", self)

        if not self.when_connected.done():
            self.when_connected.set_exception(
                AccessoryDisconnectedError(
                    'Current connection attempt failed and will be retried',
                )
            )

        self.when_connected = asyncio.Future()

        if self.auto_reconnect and not self.closing:
            asyncio.ensure_future(self._reconnect())

        if self.closing or not self.auto_reconnect:
            self.closed = True

    async def _connect_once(self):
        loop = asyncio.get_event_loop()
        self.transport, self.protocol = await loop.create_connection(
            lambda: InsecureHomeKitProtocol(self),
            self.host,
            self.port
        )

        if self.owner:
            await self.owner.connection_made(False)

    async def _reconnect(self):
        # FIXME: How to integrate discovery here?
        # There is aiozeroconf but that doesn't work on Windows until python 3.9
        # In HASS, zeroconf is a service provided by HASS itself and want to be able to
        # leverage that instead.
        while not self.closing:
            try:
                await self._connect_once()
            except OSError:
                interval = self._retry_interval = min(60, 1.5 * self._retry_interval)
                logger.info("Connecting to accessory failed. Retrying in %i seconds", interval)
                await asyncio.sleep(interval)
                continue

            self._retry_interval = 0.5
            self.when_connected.set_result(None)
            return

    def event_received(self, event):
        if not self.owner:
            return

        # FIXME: Should drop the connection if can't parse the event?

        decoded = event.body.decode('utf-8')
        if not decoded:
            return

        try:
            parsed = json.loads(decoded)
        except json.JSONDecodeError:
            return

        self.owner.event_received(parsed)

    def __repr__(self):
        return "HomeKitConnection(host=%r, port=%r)" % (self.host, self.port)


class SecureHomeKitConnection(HomeKitConnection):

    def __init__(self, owner, pairing_data):
        super().__init__(
            owner,
            pairing_data['AccessoryIP'],
            pairing_data['AccessoryPort'],
        )
        self.pairing_data = pairing_data

    async def _connect_once(self):
        await super()._connect_once()

        state_machine = get_session_keys(self.pairing_data)

        request, expected = state_machine.send(None)
        while True:
            try:
                response = await self.post_tlv(
                    '/pair-verify',
                    body=request,
                    expected=expected,
                )
                request, expected = state_machine.send(response)
            except StopIteration as result:
                # If the state machine raises a StopIteration then we have session keys
                c2a_key, a2c_key = result.value
                break

        # Secure session has been negotiated - switch protocol so all future messages are encrypted
        self.protocol = SecureHomeKitProtocol(
            self,
            a2c_key,
            c2a_key,
        )
        self.transport.set_protocol(self.protocol)
        self.protocol.connection_made(self.transport)

        if self.owner:
            await self.owner.connection_made(True)
