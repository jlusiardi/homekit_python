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

from http.server import BaseHTTPRequestHandler
import binascii
import io
import json
import gmpy2
import py25519
import hkdf
import hashlib
import sys
import socket
import select

from homekit.tlv import TLV
from homekit.srp import SrpServer
from homekit.chacha20poly1305 import chacha20_aead_encrypt, chacha20_aead_decrypt
from homekit.statuscodes import HttpStatusCodes, HapStatusCodes
from homekit.exception import HomeKitStatusException


def bytes_to_mpz(input_bytes):
    return gmpy2.mpz(binascii.hexlify(input_bytes), 16)


class HomeKitRequestHandler(BaseHTTPRequestHandler):
    VALID_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE']
    DEBUG_PUT_CHARACTERISTICS = False
    DEBUG_CRYPT = False
    DEBUG_PAIR_VERIFY = False
    DEBUG_GET_CHARACTERISTICS = False
    timeout = 300

    def __init__(self, request, client_address, server):
        # keep pycharm from complaining about those not being define in __init__
        # self.session_id = '{ip}:{port}'.format(ip=client_address[0], port= client_address[1])
        self.session_id = '{ip}'.format(ip=client_address[0])
        if self.session_id not in server.sessions:
            server.sessions[self.session_id] = {'handler': self}
        self.rfile = None
        self.wfile = None
        self.body = None
        self.PATHMAPPING = {
            '/accessories': {
                'GET': self._get_accessories
            },
            '/characteristics': {
                'GET': self._get_characteristics,
                'PUT': self._put_characteristics
            },
            '/identify': {
                'POST': self._post_identify
            },
            '/pair-setup': {
                'POST': self._post_pair_setup
            },
            '/pair-verify': {
                'POST': self._post_pair_verify
            },
            '/pairings': {
                'POST': self._post_pairings
            }
        }
        self.protocol_version = 'HTTP/1.1'
        self.close_connection = False

        self.timeout_counter = 0

        # init super class
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    def handle_one_request(self):
        """
        This is used to determine wether the request is encrypted or not. This is done by looking at the first bytes of
        the request. To be valid unencrypted HTTP call, it must be one of the methods defined in RFC7231 Section 4
        "Request Methods".
        :return:
        """
        try:
            # make connection non blocking so the select can work
            self.connection.setblocking(0)
            ready = select.select([self.connection], [], [], 1)

            # no data was to be received, so we count up to track how many seconds in total this happened
            if not ready[0]:
                self.timeout_counter += 1

                # if this is above our configured timeout the connection gets closed
                if self.timeout_counter >= self.timeout:
                    self.close_connection = True
                return

            raw_peeked_data = self.rfile.peek(10)
            if len(raw_peeked_data) == 0:
                # since select says ready but no data is there, close the connection to prevent hidden busy waiting to
                # rise load
                self.close_connection = True
                return

            # data was received so reset the timeout handler
            self.timeout_counter = 0

            # RFC7230 Section 3 tells us, that US-ASCII is fine
            peeked_data = raw_peeked_data[:10]
            peeked_data = peeked_data.decode(encoding='ASCII')
            # self.log_message('deciding over: >%s<', peeked_data)
            # If the request line starts with a known HTTP verb, then use handle_one_request from super class
            if ' ' in peeked_data:
                method = peeked_data.split(' ', 1)[0]
                if method in self.VALID_METHODS:
                    self.server.sessions[self.session_id]['enrypted_connection'] = False
                    BaseHTTPRequestHandler.handle_one_request(self)
                    return
        except (socket.timeout, OSError) as e:
            # a read or a write timed out.  Discard this connection
            self.log_error(' %r', e)
            self.close_connection = True
            return
        except UnicodeDecodeError as e:
            # self.log_error('exception %s' % e)
            pass

        # the first 2 bytes are the length of the encrypted data to follow
        len_bytes = self.rfile.read(2)
        data_len = int.from_bytes(len_bytes, byteorder='little')

        # the authtag is not counted, so add its length
        data = self.rfile.read(data_len + 16)
        if HomeKitRequestHandler.DEBUG_CRYPT:
            self.log_message('data >%i< >%s<', len(data), binascii.hexlify(data))

        # get the crypto key from the session
        c2a_key = self.server.sessions[self.session_id]['controller_to_accessory_key']

        # verify & decrypt the read data
        cnt_bytes = self.server.sessions[self.session_id]['controller_to_accessory_count'].to_bytes(8,
                                                                                                    byteorder='little')
        decrypted = chacha20_aead_decrypt(len_bytes, c2a_key, cnt_bytes, bytes([0, 0, 0, 0]),
                                          data)
        if decrypted == False:
            self.log_error('Could not decrypt %s', binascii.hexlify(data))
            # TODO: handle errors
            pass

        if HomeKitRequestHandler.DEBUG_CRYPT:
            self.log_message('crypted request >%s<', decrypted)

        self.server.sessions[self.session_id]['controller_to_accessory_count'] += 1

        # replace the original rfile with a fake with the decrypted stuff
        old_rfile = self.rfile
        self.rfile = io.BytesIO(decrypted)

        # replace writefile to pass on encrypted data
        old_wfile = self.wfile
        self.wfile = io.BytesIO()

        # call known function
        self.server.sessions[self.session_id]['enrypted_connection'] = True
        BaseHTTPRequestHandler.handle_one_request(self)

        # read the plaintext and send it out encrypted
        self.wfile.seek(0)
        in_data = self.wfile.read(65537)

        if HomeKitRequestHandler.DEBUG_CRYPT:
            self.log_message('response >%s<', in_data)
            self.log_message('len(response) %s', len(in_data))

        block_size = 1024
        out_data = bytearray()
        while len(in_data) > 0:
            block = in_data[:block_size]
            if HomeKitRequestHandler.DEBUG_CRYPT:
                self.log_message('==> BLOCK: len %s', len(block))
            in_data = in_data[block_size:]

            len_bytes = len(block).to_bytes(2, byteorder='little')
            a2c_key = self.server.sessions[self.session_id]['accessory_to_controller_key']
            cnt_bytes = self.server.sessions[self.session_id]['accessory_to_controller_count'].to_bytes(8,
                                                                                                        byteorder='little')
            ciper_and_mac = chacha20_aead_encrypt(len_bytes, a2c_key, cnt_bytes, bytes([0, 0, 0, 0]), block)
            self.server.sessions[self.session_id]['accessory_to_controller_count'] += 1
            out_data += len_bytes + ciper_and_mac[0] + ciper_and_mac[1]

        # change back to originals to handle multiple calls
        self.rfile = old_rfile
        self.wfile = old_wfile

        # send data to original requester
        self.wfile.write(out_data)
        self.wfile.flush()

    def _get_characteristics(self):
        """
        As described on page 84
        :return:
        """
        if HomeKitRequestHandler.DEBUG_GET_CHARACTERISTICS:
            self.log_message('GET /characteristics')

        # analyse
        params = {}
        if '?' in self.path:
            params = {t.split('=')[0]: t.split('=')[1] for t in self.path.split('?')[1].split('&')}

        # handle id param
        ids = []
        if 'id' in params:
            ids = params['id'].split(',')

        # handle meta param
        meta = False
        if 'meta' in params:
            meta = params['meta'] == 1

        # handle perms param
        perms = False
        if 'perms' in params:
            perms = params['perms'] == 1

        # handle type param
        type = False
        if 'type' in params:
            type = params['type'] == 1

        # handle ev param
        ev = False
        if 'ev' in params:
            ev = params['ev'] == 1

        if HomeKitRequestHandler.DEBUG_GET_CHARACTERISTICS:
            self.log_message('query parameters: ids: %s, meta: %s, perms: %s, type: %s, ev: %s', ids, meta, perms, type,
                             ev)

        result = {
            'characteristics': []
        }

        errors = 0
        for id_pair in ids:
            id_pair = id_pair.split('.')
            aid = int(id_pair[0])
            cid = int(id_pair[1])
            found = False
            for accessory in self.server.accessories.accessories:
                if accessory.aid != aid:
                    continue
                for service in accessory.services:
                    for characteristic in service.characteristics:
                        if characteristic.iid != cid:
                            continue
                        found = True
                        # try to read the characteristic and report possible exceptions as error
                        try:
                            value = characteristic.get_value()
                            result['characteristics'].append({'aid': aid, 'iid': cid, 'value': value})
                        except HomeKitStatusException as e:
                            result['characteristics'].append({'aid': aid, 'iid': cid, 'status': e.status_code})
                            errors += 1
                        except Exception as e:
                            self.log_error('Exception while getting value for %s.%s: %s', aid, cid, str(e))
                            result['characteristics'].append(
                                {'aid': aid, 'iid': cid, 'status': HapStatusCodes.OUT_OF_RESOURCES})
                            errors += 1
                # report missing resources
                if not found:
                    result['characteristics'].append(
                        {'aid': aid, 'iid': cid, 'status': HapStatusCodes.RESOURCE_NOT_EXIST})
                    errors += 1

        if HomeKitRequestHandler.DEBUG_GET_CHARACTERISTICS:
            self.log_message('chars: %s', json.dumps(result))

        # set the proper status code depending on the count of characteristics and error
        if len(result['characteristics']) == errors:
            self.send_response(HttpStatusCodes.BAD_REQUEST)
        elif len(result['characteristics']) > errors > 0:
            self.send_response(HttpStatusCodes.MULTI_STATUS)
        else:
            self.send_response(HttpStatusCodes.OK)

        result_bytes = json.dumps(result).encode()
        self.send_header('Content-Type', 'application/hap+json')
        self.send_header('Content-Length', len(result_bytes))
        self.end_headers()
        self.wfile.write(result_bytes)

    def _put_characteristics(self):
        """
        Defined page 80 ff
        :return:
        """
        if HomeKitRequestHandler.DEBUG_PUT_CHARACTERISTICS:
            self.log_message('PUT /characteristics')
            self.log_message('body: %s', self.body)

        data = json.loads(self.body.decode())
        characteristics_to_set = data['characteristics']
        result = {
            'characteristics': []
        }
        errors = 0
        for characteristic_to_set in characteristics_to_set:
            aid = characteristic_to_set['aid']
            cid = characteristic_to_set['iid']
            found = False
            for accessory in self.server.accessories.accessories:
                if accessory.aid != aid:
                    continue
                for service in accessory.services:
                    for characteristic in service.characteristics:
                        if characteristic.iid != cid:
                            continue
                        found = True
                        if 'ev' in characteristic_to_set:
                            if HomeKitRequestHandler.DEBUG_PUT_CHARACTERISTICS:
                                self.log_message('set ev >%s< >%s< >%s<', aid, cid, characteristic_to_set['ev'])
                            characteristic.set_events(characteristic_to_set['ev'])

                        if 'value' in characteristic_to_set:
                            if HomeKitRequestHandler.DEBUG_PUT_CHARACTERISTICS:
                                self.log_message('set value >%s< >%s< >%s<', aid, cid, characteristic_to_set['value'])
                            try:
                                characteristic.set_value(characteristic_to_set['value'])
                                result['characteristics'].append({'aid': aid, 'iid': cid, 'status': 0})
                            except HomeKitStatusException as e:
                                result['characteristics'].append({'aid': aid, 'iid': cid, 'status': int(str(e))})
                                errors += 1
                            except Exception as e:
                                self.log_error('Exception while setting value for %s.%s: %s', aid, cid, str(e))
                                result['characteristics'].append(
                                    {'aid': aid, 'iid': cid, 'status': HapStatusCodes.OUT_OF_RESOURCES})
                                errors += 1
            # report missing resources
            if not found:
                result['characteristics'].append(
                    {'aid': aid, 'iid': cid, 'status': HapStatusCodes.RESOURCE_NOT_EXIST})
                errors += 1

        if len(result['characteristics']) == errors:
            self.send_response(HttpStatusCodes.BAD_REQUEST)
        elif len(result['characteristics']) > errors > 0:
            self.send_response(HttpStatusCodes.MULTI_STATUS)
        else:
            self.send_response(HttpStatusCodes.NO_CONTENT)
            self.end_headers()
        if errors > 0:
            result_bytes = json.dumps(result).encode()
            self.send_header('Content-Type', 'application/hap+json')
            self.send_header('Content-Length', len(result_bytes))
            self.end_headers()
            self.wfile.write(result_bytes)

    def _post_identify(self):
        if self.server.data.is_paired:
            result_bytes = json.dumps({'status': HapStatusCodes.INSUFFICIENT_PRIVILEGES}).encode()
            self.send_response(HttpStatusCodes.BAD_REQUEST)
            self.send_header('Content-Type', 'application/hap+json')
            self.send_header('Content-Length', len(result_bytes))
            self.end_headers()
            self.wfile.write(result_bytes)
        else:
            # perform identify action
            # send status code
            self.send_response(HttpStatusCodes.NO_CONTENT)
            self.end_headers()

    def _get_accessories(self):

        result_bytes = self.server.accessories.__str__().encode()
        self.send_response(HttpStatusCodes.OK)
        self.send_header('Content-Type', 'application/hap+json')
        self.send_header('Content-Length', len(result_bytes))
        self.end_headers()
        self.wfile.write(result_bytes)

    def _post_pair_verify(self):
        d_req = TLV.decode_bytes(self.body)

        d_res = {}

        if d_req[TLV.kTLVType_State] == TLV.M1:
            # step #2 Accessory -> iOS Device Verify Start Response
            if HomeKitRequestHandler.DEBUG_PAIR_VERIFY:
                self.log_message('Step #2 /pair-verify')

            # 1) generate new curve25519 key pair
            accessory_session_key = py25519.Key25519()
            accessory_spk = accessory_session_key.public_key().pubkey
            self.server.sessions[self.session_id]['accessory_pub_key'] = accessory_spk

            # 2) generate shared secret
            ios_device_curve25519_pub_key_bytes = d_req[TLV.kTLVType_PublicKey]
            self.server.sessions[self.session_id]['ios_device_pub_key'] = ios_device_curve25519_pub_key_bytes
            ios_device_curve25519_pub_key = py25519.Key25519(pubkey=bytes(ios_device_curve25519_pub_key_bytes),
                                                             verifyingkey=bytes())
            shared_secret = accessory_session_key.get_ecdh_key(ios_device_curve25519_pub_key)
            self.server.sessions[self.session_id]['shared_secret'] = shared_secret

            # 3) generate accessory info
            accessory_info = accessory_spk + self.server.data.accessory_pairing_id_bytes + \
                             ios_device_curve25519_pub_key_bytes

            # 4) sign accessory info for accessory signature
            accessory_ltsk = py25519.Key25519(secretkey=self.server.data.accessory_ltsk)
            accessory_signature = accessory_ltsk.sign(accessory_info)

            # 5) sub tlv
            sub_tlv = {
                TLV.kTLVType_Identifier: self.server.data.accessory_pairing_id_bytes,
                TLV.kTLVType_Signature: accessory_signature
            }
            sub_tlv_b = TLV.encode_dict(sub_tlv)

            # 6) derive session key
            hkdf_inst = hkdf.Hkdf('Pair-Verify-Encrypt-Salt'.encode(), shared_secret, hash=hashlib.sha512)
            session_key = hkdf_inst.expand('Pair-Verify-Encrypt-Info'.encode(), 32)
            self.server.sessions[self.session_id]['session_key'] = session_key

            # 7) encrypt sub tlv
            encrypted_data_with_auth_tag = chacha20_aead_encrypt(bytes(),
                                                                 session_key,
                                                                 'PV-Msg02'.encode(),
                                                                 bytes([0, 0, 0, 0]),
                                                                 sub_tlv_b)
            tmp = bytearray(encrypted_data_with_auth_tag[0])
            tmp += encrypted_data_with_auth_tag[1]

            # 8) construct result tlv
            d_res[TLV.kTLVType_State] = TLV.M2
            d_res[TLV.kTLVType_PublicKey] = accessory_spk
            d_res[TLV.kTLVType_EncryptedData] = tmp

            self._send_response_tlv(d_res)
            if HomeKitRequestHandler.DEBUG_PAIR_VERIFY:
                self.log_message('after step #2\n%s', TLV.to_string(d_res))
            return

        if d_req[TLV.kTLVType_State] == TLV.M3:
            # step #4 Accessory -> iOS Device Verify Finish Response
            if HomeKitRequestHandler.DEBUG_PAIR_VERIFY:
                self.log_message('Step #4 /pair-verify')

            session_key = self.server.sessions[self.session_id]['session_key']

            # 1) verify ios' authtag
            # 2) decrypt
            encrypted = d_req[TLV.kTLVType_EncryptedData]
            decrypted = chacha20_aead_decrypt(bytes(), session_key, 'PV-Msg03'.encode(), bytes([0, 0, 0, 0]),
                                              encrypted)
            if decrypted == False:
                self.send_error_reply(TLV.M4, TLV.kTLVError_Authentication)
                print('error in step #4: authtag', d_res, self.server.sessions)
                return
            d1 = TLV.decode_bytes(decrypted)
            assert TLV.kTLVType_Identifier in d1
            assert TLV.kTLVType_Signature in d1

            # 3) get ios_device_ltpk
            ios_device_pairing_id = d1[TLV.kTLVType_Identifier]
            self.server.sessions[self.session_id]['ios_device_pairing_id'] = ios_device_pairing_id
            ios_device_ltpk_bytes = self.server.data.get_peer_key(ios_device_pairing_id)
            if ios_device_ltpk_bytes is None:
                self.send_error_reply(TLV.M4, TLV.kTLVError_Authentication)
                print('error in step #4: not paired', d_res, self.server.sessions)
                return
            ios_device_ltpk = py25519.Key25519(pubkey=bytes(), verifyingkey=ios_device_ltpk_bytes)

            # 4) verify ios_device_info
            ios_device_sig = d1[TLV.kTLVType_Signature]
            ios_device_curve25519_pub_key_bytes = self.server.sessions[self.session_id]['ios_device_pub_key']
            accessory_spk = self.server.sessions[self.session_id]['accessory_pub_key']
            ios_device_info = ios_device_curve25519_pub_key_bytes + ios_device_pairing_id + accessory_spk
            if not ios_device_ltpk.verify(bytes(ios_device_sig), bytes(ios_device_info)):
                self.send_error_reply(TLV.M4, TLV.kTLVError_Authentication)
                print('error in step #4: signature', d_res, self.server.sessions)
                return

            #
            shared_secret = self.server.sessions[self.session_id]['shared_secret']
            hkdf_inst = hkdf.Hkdf('Control-Salt'.encode(), shared_secret, hash=hashlib.sha512)
            controller_to_accessory_key = hkdf_inst.expand('Control-Write-Encryption-Key'.encode(), 32)
            self.server.sessions[self.session_id]['controller_to_accessory_key'] = controller_to_accessory_key
            self.server.sessions[self.session_id]['controller_to_accessory_count'] = 0

            hkdf_inst = hkdf.Hkdf('Control-Salt'.encode(), shared_secret, hash=hashlib.sha512)
            accessory_to_controller_key = hkdf_inst.expand('Control-Read-Encryption-Key'.encode(), 32)
            self.server.sessions[self.session_id]['accessory_to_controller_key'] = accessory_to_controller_key
            self.server.sessions[self.session_id]['accessory_to_controller_count'] = 0

            d_res[TLV.kTLVType_State] = TLV.M4

            self._send_response_tlv(d_res)
            if HomeKitRequestHandler.DEBUG_PAIR_VERIFY:
                self.log_message('after step #4\n%s', TLV.to_string(d_res))
            return

        self.send_error(HttpStatusCodes.METHOD_NOT_ALLOWED)

    def _post_pairings(self):
        d_req = TLV.decode_bytes(self.body)
        self.log_message('POST /pairings request body:\n%s', TLV.to_string(d_req))

        session = self.server.sessions[self.session_id]
        server_data = self.server.data

        d_res = {}

        if d_req[TLV.kTLVType_State] == TLV.M1 and d_req[TLV.kTLVType_Method] == TLV.AddPairing:
            self.log_message('Step #2 /pairings add pairing')
            # see page 51
            self.send_error(HttpStatusCodes.METHOD_NOT_ALLOWED)
            return

        if d_req[TLV.kTLVType_State] == TLV.M1 and d_req[TLV.kTLVType_Method] == TLV.RemovePairing:
            # step #2 Accessory -> iOS Device remove pairing response
            self.log_message('Step #2 /pairings remove pairings')

            # 1)

            # 2) verify set admin bit
            ios_device_pairing_id = session['ios_device_pairing_id']
            if not server_data.is_peer_admin(ios_device_pairing_id):
                self.send_error_reply(TLV.M2, TLV.kTLVError_Authentication)
                print('error in step #2: admin bit')
                return

            # 3) remove pairing and republish device
            server_data.remove_peer(d_req[TLV.kTLVType_Identifier])
            self.server.publish_device()

            d_res[TLV.kTLVType_State] = TLV.M2
            self._send_response_tlv(d_res)
            self.log_message('after step #2\n%s', TLV.to_string(d_res))
            return

        if d_req[TLV.kTLVType_State] == TLV.M1 and d_req[TLV.kTLVType_Method] == TLV.ListPairings:
            # step #2 Accessory -> iOS Device list pairing response
            self.log_message('Step #2 /pairings list pairings')

            # 1) Validate against session

            # 2) verify set admin bit
            ios_device_pairing_id = session['ios_device_pairing_id']
            if not server_data.is_peer_admin(ios_device_pairing_id):
                self.send_error_reply(TLV.M2, TLV.kTLVError_Authentication)
                print('error in step #2: admin bit')
                return

            # 3) construct response TLV
            tmp = [(TLV.kTLVType_State, TLV.M2)]
            for index, pairing_id in enumerate(server_data.peers):
                tmp.append((TLV.kTLVType_Identifier, pairing_id.encode()))
                tmp.append((TLV.kTLVType_PublicKey, server_data.get_peer_key(pairing_id.encode())))
                user = TLV.kTLVType_Permission_RegularUser
                if server_data.is_peer_admin(pairing_id.encode()):
                    user = TLV.kTLVType_Permission_AdminUser
                tmp.append((TLV.kTLVType_Permissions, user))
                if index + 1 < len(server_data.peers):
                    tmp.append((TLV.kTLVType_Separator, bytes(0)))
            result_bytes = TLV.encode_list(tmp)

            # 4) send response
            self.send_response(HttpStatusCodes.OK)
            # Send headers
            self.send_header('Content-Length', len(result_bytes))
            self.send_header('Content-Type', 'application/pairing+tlv8')
            self.send_header('Connection', 'keep-alive')
            self.end_headers()

            self.wfile.write(result_bytes)
            return

        self.send_error(HttpStatusCodes.METHOD_NOT_ALLOWED)

    def send_error_reply(self, state, error):
        """
        Send an error reply encoded as TLV.
        :param state: The state as in TLV.M1, TLV.M2, ...
        :param error: The error code as in TLV.kTLVError_*
        :return: None
        """
        d_res = dict()
        d_res[TLV.kTLVType_State] = state
        d_res[TLV.kTLVType_Error] = error
        result_bytes = TLV.encode_dict(d_res)

        self.send_response(HttpStatusCodes.METHOD_NOT_ALLOWED)
        # Send headers
        self.send_header('Content-Length', len(result_bytes))
        self.send_header('Content-Type', 'application/pairing+tlv8')
        self.end_headers()

        self.wfile.write(result_bytes)

    def _post_pair_setup(self):
        d_req = TLV.decode_bytes(self.body)
        self.log_message('POST /pair-setup request body:\n%s', TLV.to_string(d_req))

        d_res = {}

        if d_req[TLV.kTLVType_State] == TLV.M1:
            # step #2 Accessory -> iOS Device SRP Start Response
            self.log_message('Step #2 /pair-setup')

            # 1) Check if paired
            if self.server.data.is_paired:
                self.send_error_reply(TLV.M2, TLV.kTLVError_Unavailable)
                return

            # 2) Check if over 100 attempts
            if self.server.data.unsuccessful_tries > 100:
                self.log_error('to many failed attempts')
                self.send_error_reply(TLV.M2, TLV.kTLVError_MaxTries)
                return

            # 3) Check if already in pairing
            if False:
                self.send_error_reply(TLV.M2, TLV.kTLVError_Busy)
                return

            # 4) 5) 7) Create in SRP Session, set username and password
            server = SrpServer('Pair-Setup', self.server.data.setup_code)

            # 6) create salt
            salt = server.get_salt()

            # 8) show setup code to user
            sc = self.server.data.setup_code
            sc_str = 'Setup Code\n┌─' + '─' * len(sc) + '─┐\n│ ' + sc + ' │\n└─' + '─' * len(sc) + '─┘'
            self.log_message(sc_str)

            # 9) create public key
            public_key = server.get_public_key()

            # 10) create response tlv and send response
            d_res[TLV.kTLVType_State] = TLV.M2
            d_res[TLV.kTLVType_PublicKey] = SrpServer.to_byte_array(public_key)
            d_res[TLV.kTLVType_Salt] = SrpServer.to_byte_array(salt)
            self._send_response_tlv(d_res)

            # store session
            self.server.sessions[self.session_id]['srp'] = server
            self.log_message('after step #2:\n%s', TLV.to_string(d_res))
            return

        if d_req[TLV.kTLVType_State] == TLV.M3:
            # step #4 Accessory -> iOS Device SRP Verify Response
            self.log_message('Step #4 /pair-setup')

            # 1) use ios pub key to compute shared secret key
            ios_pub_key = bytes_to_mpz(d_req[TLV.kTLVType_PublicKey])
            server = self.server.sessions[self.session_id]['srp']
            server.set_client_public_key(ios_pub_key)

            hkdf_inst = hkdf.Hkdf('Pair-Setup-Encrypt-Salt'.encode(), SrpServer.to_byte_array(server.get_session_key()),
                                  hash=hashlib.sha512)
            session_key = hkdf_inst.expand('Pair-Setup-Encrypt-Info'.encode(), 32)
            self.server.sessions[self.session_id]['session_key'] = session_key

            # 2) verify ios proof
            ios_proof = bytes_to_mpz(d_req[TLV.kTLVType_Proof])
            if not server.verify_clients_proof(ios_proof):
                d_res[TLV.kTLVType_State] = TLV.M4
                d_res[TLV.kTLVType_Error] = TLV.kTLVError_Authentication

                self._send_response_tlv(d_res)
                print('error in step #4', d_res, self.server.sessions)
                return
            else:
                self.log_message('ios proof was verified')

            # 3) generate accessory proof
            accessory_proof = server.get_proof(ios_proof)

            # 4) create response tlv
            d_res[TLV.kTLVType_State] = TLV.M4
            d_res[TLV.kTLVType_Proof] = SrpServer.to_byte_array(accessory_proof)

            # 5) send response tlv
            self._send_response_tlv(d_res)

            self.log_message('after step #4:\n%s', TLV.to_string(d_res))
            return

        if d_req[TLV.kTLVType_State] == TLV.M5:
            # step #6 Accessory -> iOS Device Exchange Response
            self.log_message('Step #6 /pair-setup')

            # 1) Verify the iOS device's authTag
            # done by chacha20_aead_decrypt

            # 2) decrypt and test
            encrypted_data = d_req[TLV.kTLVType_EncryptedData]
            decrypted_data = chacha20_aead_decrypt(bytes(), self.server.sessions[self.session_id]['session_key'],
                                                   'PS-Msg05'.encode(), bytes([0, 0, 0, 0]),
                                                   encrypted_data)
            if decrypted_data == False:
                d_res[TLV.kTLVType_State] = TLV.M6
                d_res[TLV.kTLVType_Error] = TLV.kTLVError_Authentication

                self.send_error_reply(TLV.M6, TLV.kTLVError_Authentication)
                print('error in step #6', d_res, self.server.sessions)
                return

            d_req_2 = TLV.decode_bytearray(decrypted_data)

            # 3) Derive ios_device_x
            shared_secret = self.server.sessions[self.session_id]['srp'].get_session_key()
            hkdf_inst = hkdf.Hkdf('Pair-Setup-Controller-Sign-Salt'.encode(), SrpServer.to_byte_array(shared_secret),
                                  hash=hashlib.sha512)
            ios_device_x = hkdf_inst.expand('Pair-Setup-Controller-Sign-Info'.encode(), 32)

            # 4) construct ios_device_info
            ios_device_pairing_id = d_req_2[TLV.kTLVType_Identifier]
            ios_device_ltpk = d_req_2[TLV.kTLVType_PublicKey]
            ios_device_info = ios_device_x + ios_device_pairing_id + ios_device_ltpk

            # 5) verify signature
            ios_device_sig = d_req_2[TLV.kTLVType_Signature]

            verify_key = py25519.Key25519(pubkey=bytes(), verifyingkey=bytes(ios_device_ltpk))
            if not verify_key.verify(bytes(ios_device_sig), bytes(ios_device_info)):
                self.send_error_reply(TLV.M6, TLV.kTLVError_Authentication)
                print('error in step #6', d_res, self.server.sessions)
                return

            # 6) save ios_device_pairing_id and ios_device_ltpk
            self.server.data.add_peer(ios_device_pairing_id, ios_device_ltpk)

            # Response Generation
            # 1) generate accessoryLTPK if not existing
            if self.server.data.accessory_ltsk is None or self.server.data.accessory_ltpk is None:
                accessory_ltsk = py25519.Key25519()
                accessory_ltpk = accessory_ltsk.verifyingkey
                self.server.data.set_accessory_keys(accessory_ltpk, accessory_ltsk.secretkey)
            else:
                accessory_ltsk = py25519.Key25519(self.server.data.accessory_ltsk)
                accessory_ltpk = accessory_ltsk.verifyingkey

            # 2) derive AccessoryX
            hkdf_inst = hkdf.Hkdf('Pair-Setup-Accessory-Sign-Salt'.encode(), SrpServer.to_byte_array(shared_secret),
                                  hash=hashlib.sha512)
            accessory_x = hkdf_inst.expand('Pair-Setup-Accessory-Sign-Info'.encode(), 32)

            # 3)
            accessory_info = accessory_x + self.server.data.accessory_pairing_id_bytes + accessory_ltpk

            # 4) generate signature
            accessory_signature = accessory_ltsk.sign(accessory_info)

            # 5) construct sub_tlv
            sub_tlv = {
                TLV.kTLVType_Identifier: self.server.data.accessory_pairing_id_bytes,
                TLV.kTLVType_PublicKey: accessory_ltpk,
                TLV.kTLVType_Signature: accessory_signature
            }
            sub_tlv_b = TLV.encode_dict(sub_tlv)

            # 6) encrypt sub_tlv
            encrypted_data_with_auth_tag = chacha20_aead_encrypt(bytes(),
                                                                 self.server.sessions[self.session_id]['session_key'],
                                                                 'PS-Msg06'.encode(),
                                                                 bytes([0, 0, 0, 0]),
                                                                 sub_tlv_b)
            tmp = bytearray(encrypted_data_with_auth_tag[0])
            tmp += encrypted_data_with_auth_tag[1]

            # 7) send response
            self.server.publish_device()
            d_res = dict()
            d_res[TLV.kTLVType_State] = TLV.M6
            d_res[TLV.kTLVType_EncryptedData] = tmp

            self._send_response_tlv(d_res)
            self.log_message('after step #6:\n%s', TLV.to_string(d_res))
            return

        self.send_error(HttpStatusCodes.METHOD_NOT_ALLOWED)

    def _send_response_tlv(self, d_res, close=False, status=HttpStatusCodes.OK):
        result_bytes = TLV.encode_dict(d_res)

        self.send_response(status)
        # Send headers
        self.send_header('Content-Length', len(result_bytes))
        self.send_header('Content-Type', 'application/pairing+tlv8')
        self.send_header('Connection', 'keep-alive')
        self.end_headers()

        self.wfile.write(result_bytes)

    class Wrapper:
        """
        Wraps a bytes or bytearray data into a file like object.
        """

        def __init__(self, data):
            self.data = data

        def makefile(self, arg):
            return io.BytesIO(self.data)

    def do_GET(self):
        """
        Can use
            * command
            * headers
            * path
            * ...
        :return:
        """
        absolute_path = self.path.split('?')[0]
        if absolute_path in self.PATHMAPPING:
            if 'GET' in self.PATHMAPPING[absolute_path]:
                # self.log_message('-' * 80 + '\ndo_GET / path: %s', self.path)
                self.PATHMAPPING[absolute_path]['GET']()
                return
        self.log_error('send error because of unmapped path: %s', self.path)
        self.send_error(HttpStatusCodes.NOT_FOUND)

    def do_POST(self):
        # read the body identified by its length
        content_length = int(self.headers['Content-Length'])
        self.body = self.rfile.read(content_length)
        if self.path in self.PATHMAPPING:
            if 'POST' in self.PATHMAPPING[self.path]:
                # self.log_message('-' * 80 + '\ndo_POST / path: %s', self.path)
                self.PATHMAPPING[self.path]['POST']()
                return
        self.log_error('send error because of unmapped path: %s', self.path)
        self.send_error(HttpStatusCodes.NOT_FOUND)

    def do_PUT(self):
        # read the body identified by its length
        content_length = int(self.headers['Content-Length'])
        self.body = self.rfile.read(content_length)
        if self.path in self.PATHMAPPING:
            if 'PUT' in self.PATHMAPPING[self.path]:
                # self.log_message('-' * 80 + '\ndo_PUT / path: %s', self.path)
                self.PATHMAPPING[self.path]['PUT']()
                return
        self.log_error('send error because of unmapped path: %s', self.path)
        self.send_error(HttpStatusCodes.NOT_FOUND)

    def log_message(self, format, *args):
        if self.server.logger is None:
            pass
        elif self.server.logger == sys.stderr:
            BaseHTTPRequestHandler.log_message(self, format, *args)
        else:
            self.server.logger.info("%s" % (format % args))

    def log_error(self, format, *args):
        if self.server.logger is None:
            pass
        elif self.server.logger == sys.stderr:
            BaseHTTPRequestHandler.log_error(self, format, *args)
        else:
            self.server.logger.error("%s" % (format % args))
