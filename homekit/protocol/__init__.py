#
# Copyright 2018-2020 Joachim Lusiardi
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

import hashlib
import ed25519
import hkdf
from binascii import hexlify
import logging
import tlv8

from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import serialization

from homekit.protocol.tlv import Steps, Methods, Errors, Types
from homekit.exceptions import IncorrectPairingIdError, InvalidAuthTagError, InvalidSignatureError, UnavailableError, \
    AuthenticationError, InvalidError, BusyError, MaxTriesError, MaxPeersError, BackoffError

import homekit.exceptions
from homekit.crypto import chacha20_aead_decrypt, chacha20_aead_encrypt, SrpClient


def error_handler(error, stage):
    """
    Transform the various error messages defined in table 4-5 page 60 into exceptions

    :param error: the kind of error
    :param stage: the stage it appeared in
    :return: None
    """
    if error == Errors.kTLVError_Unavailable:
        raise UnavailableError(stage)
    elif error == Errors.kTLVError_Authentication:
        raise AuthenticationError(stage)
    elif error == Errors.TLVError_Backoff:
        raise BackoffError(stage)
    elif error == Errors.kTLVError_MaxPeers:
        raise MaxPeersError(stage)
    elif error == Errors.kTLVError_MaxTries:
        raise MaxTriesError(stage)
    elif error == Errors.kTLVError_Busy:
        raise BusyError(stage)
    else:
        raise InvalidError(stage)


def create_ip_pair_setup_write(connection):
    def write_http(request, expected):
        body = tlv8.encode(request)
        logging.debug('write message: %s', tlv8.format_string(tlv8.decode(body)))
        connection.putrequest('POST', '/pair-setup', skip_accept_encoding=True)
        connection.putheader('Content-Type', 'application/pairing+tlv8')
        connection.putheader('Content-Length', len(body))
        connection.endheaders(body)
        resp = connection.getresponse()
        body = resp.read()
        response_tlv = tlv8.decode(body, expected)
        logging.debug('response: %s', tlv8.format_string(response_tlv))
        return response_tlv

    return write_http


def create_ip_pair_verify_write(connection):
    def write_http(request, expected):
        body = tlv8.encode(request)
        logging.debug('write message: %s', tlv8.format_string(tlv8.decode(body)))
        connection.putrequest('POST', '/pair-verify', skip_accept_encoding=True)
        connection.putheader('Content-Type', 'application/pairing+tlv8')
        connection.putheader('Content-Length', len(body))
        connection.endheaders(body)
        resp = connection.getresponse()
        body = resp.read()
        response_tlv = tlv8.decode(body, expected)
        logging.debug('response: %s', tlv8.format_string(response_tlv))
        return response_tlv

    return write_http


def perform_pair_setup_part1():
    """
    Performs a pair setup operation as described in chapter 4.7 page 39 ff.

    :return: a tuple of salt and server's public key
    :raises UnavailableError: if the device is already paired
    :raises MaxTriesError: if the device received more than 100 unsuccessful pairing attempts
    :raises BusyError: if a parallel pairing is ongoing
    :raises AuthenticationError: if the verification of the device's SRP proof fails
    :raises MaxPeersError: if the device cannot accept an additional pairing
    :raises IllegalData: if the verification of the accessory's data fails
    """

    #
    # Step #1 ios --> accessory (send SRP start Request) (see page 39)
    #
    logging.debug('#1 ios -> accessory: send SRP start request')
    request_tlv = [
        tlv8.Entry(Types.kTLVType_State, Steps.M1),
        tlv8.Entry(Types.kTLVType_Method, Methods.PairSetup)
    ]

    step2_expectations = {
        Types.kTLVType_State: tlv8.DataType.INTEGER,
        Types.kTLVType_Error: tlv8.DataType.INTEGER,
        Types.kTLVType_PublicKey: tlv8.DataType.BYTES,
        Types.kTLVType_Salt: tlv8.DataType.BYTES
    }
    response_tlv = yield (request_tlv, step2_expectations)

    #
    # Step #3 ios --> accessory (send SRP verify request) (see page 41)
    #
    logging.debug('#3 ios -> accessory: send SRP verify request')

    response_tlv.assert_has(Types.kTLVType_State, 'perform_pair_setup: no state given')
    assert response_tlv.first_by_id(Types.kTLVType_State).data == Steps.M2, 'perform_pair_setup: State not M2'

    # the errors here can be:
    #  * kTLVError_Unavailable: Device is paired
    #  * kTLVError_MaxTries: More than 100 unsuccessful attempts
    #  * kTLVError_Busy: There is already a pairing going on
    error = response_tlv.first_by_id(Types.kTLVType_Error)
    if error is not None:
        error_handler(error.data, 'step 3')

    response_tlv.assert_has(Types.kTLVType_PublicKey, 'perform_pair_setup: Not a public key')
    response_tlv.assert_has(Types.kTLVType_Salt, 'perform_pair_setup: Not a salt')

    return response_tlv.first_by_id(Types.kTLVType_Salt).data, response_tlv.first_by_id(Types.kTLVType_PublicKey).data


def perform_pair_setup_part2(pin, ios_pairing_id, salt, server_public_key):
    """
    Performs a pair setup operation as described in chapter 4.7 page 39 ff.

    :param pin: the setup code from the accessory
    :param ios_pairing_id: the id of the simulated ios device
    :return: a dict with the ios device's part of the pairing information
    :raises UnavailableError: if the device is already paired
    :raises MaxTriesError: if the device received more than 100 unsuccessful pairing attempts
    :raises BusyError: if a parallel pairing is ongoing
    :raises AuthenticationError: if the verification of the device's SRP proof fails
    :raises MaxPeersError: if the device cannot accept an additional pairing
    :raises IllegalData: if the verification of the accessory's data fails
    """

    srp_client = SrpClient('Pair-Setup', pin)
    srp_client.set_salt(salt)
    srp_client.set_server_public_key(server_public_key)
    client_pub_key = srp_client.get_public_key()
    client_proof = srp_client.get_proof()

    response_tlv = [
        tlv8.Entry(Types.kTLVType_State, Steps.M3),
        tlv8.Entry(Types.kTLVType_PublicKey, SrpClient.to_byte_array(client_pub_key)),
        tlv8.Entry(Types.kTLVType_Proof, SrpClient.to_byte_array(client_proof)),
    ]

    step4_expectations = {
        Types.kTLVType_State: tlv8.DataType.INTEGER,
        Types.kTLVType_Error: tlv8.DataType.INTEGER,
        Types.kTLVType_Proof: tlv8.DataType.BYTES
    }
    response_tlv = yield (response_tlv, step4_expectations)

    #
    # Step #5 ios --> accessory (Exchange Request) (see page 43)
    #
    logging.debug('#5 ios -> accessory: send SRP exchange request')

    # M4 Verification (page 43)
    # response_tlv = TLV.reorder(response_tlv, step4_expectations)
    assert response_tlv[0].type_id == Types.kTLVType_State and response_tlv[0].data == Steps.M4, \
        'perform_pair_setup: State not M4'
    if response_tlv[1].type_id == Types.kTLVType_Error:
        error_handler(response_tlv[1].data, 'step 5')

    assert response_tlv[1].type_id == Types.kTLVType_Proof, 'perform_pair_setup: Not a proof'
    if not srp_client.verify_servers_proof(response_tlv[1].data):
        raise AuthenticationError('Step #5: wrong proof!')

    # M5 Request generation (page 44)
    session_key = srp_client.get_session_key()

    ios_device_ltsk, ios_device_ltpk = ed25519.create_keypair()

    # reversed:
    #   Pair-Setup-Encrypt-Salt instead of Pair-Setup-Controller-Sign-Salt
    #   Pair-Setup-Encrypt-Info instead of Pair-Setup-Controller-Sign-Info
    hkdf_inst = hkdf.Hkdf('Pair-Setup-Controller-Sign-Salt'.encode(), SrpClient.to_byte_array(session_key),
                          hash=hashlib.sha512)
    ios_device_x = hkdf_inst.expand('Pair-Setup-Controller-Sign-Info'.encode(), 32)

    hkdf_inst = hkdf.Hkdf('Pair-Setup-Encrypt-Salt'.encode(), SrpClient.to_byte_array(session_key),
                          hash=hashlib.sha512)
    session_key = hkdf_inst.expand('Pair-Setup-Encrypt-Info'.encode(), 32)

    ios_device_pairing_id = ios_pairing_id.encode()
    ios_device_info = ios_device_x + ios_device_pairing_id + ios_device_ltpk.to_bytes()

    ios_device_signature = ios_device_ltsk.sign(ios_device_info)

    sub_tlv = [
        tlv8.Entry(Types.kTLVType_Identifier, ios_device_pairing_id),
        tlv8.Entry(Types.kTLVType_PublicKey, ios_device_ltpk.to_bytes()),
        tlv8.Entry(Types.kTLVType_Signature, ios_device_signature)
    ]
    sub_tlv_b = tlv8.encode(sub_tlv)

    # taking tge iOSDeviceX as key was reversed from
    # https://github.com/KhaosT/HAP-NodeJS/blob/2ea9d761d9bd7593dd1949fec621ab085af5e567/lib/HAPServer.js
    # function handlePairStepFive calling encryption.encryptAndSeal
    encrypted_data_with_auth_tag = chacha20_aead_encrypt(bytes(), session_key, 'PS-Msg05'.encode(), bytes([0, 0, 0, 0]),
                                                         sub_tlv_b)
    tmp = bytearray(encrypted_data_with_auth_tag[0])
    tmp += encrypted_data_with_auth_tag[1]

    response_tlv = [
        tlv8.Entry(Types.kTLVType_State, Steps.M5),
        tlv8.Entry(Types.kTLVType_EncryptedData, tmp)
    ]

    step6_expectations = {
        Types.kTLVType_State: tlv8.DataType.INTEGER,
        Types.kTLVType_Error: tlv8.DataType.INTEGER,
        Types.kTLVType_EncryptedData: tlv8.DataType.BYTES
    }
    response_tlv = yield (response_tlv, step6_expectations)

    #
    # Step #7 ios (Verification) (page 47)
    #
    # response_tlv = TLV.reorder(response_tlv, step6_expectations)
    assert response_tlv[0].type_id == Types.kTLVType_State and response_tlv[0].data == Steps.M6, \
        'perform_pair_setup: State not M6'
    if response_tlv[1].type_id == Types.kTLVType_Error:
        error_handler(response_tlv[1].data, 'step 7')

    assert response_tlv[1].type_id == Types.kTLVType_EncryptedData, 'perform_pair_setup: No encrypted data'
    decrypted_data = bytes(chacha20_aead_decrypt(bytes(), session_key, 'PS-Msg06'.encode(), bytes([0, 0, 0, 0]),
                                                 response_tlv[1].data))
    if decrypted_data is False:
        raise homekit.exception.IllegalData('step 7')

    response_tlv = tlv8.decode(decrypted_data)
    # response_tlv = TLV.reorder(response_tlv, [
    #    Types.kTLVType_Identifier, Types.kTLVType_PublicKey, Types.kTLVType_Signature])

    #assert response_tlv[2].type_id == Types.kTLVType_Signature, 'perform_pair_setup: No signature'
    response_tlv.assert_has(Types.kTLVType_Signature, 'perform_pair_setup: No signature')
    #accessory_sig = response_tlv[2].data
    accessory_sig = response_tlv.first_by_id(Types.kTLVType_Signature).data

    assert response_tlv[0].type_id == Types.kTLVType_Identifier, 'perform_pair_setup: No identifier'
    accessory_pairing_id = response_tlv[0].data

    assert response_tlv[1].type_id == Types.kTLVType_PublicKey, 'perform_pair_setup: No public key'
    accessory_ltpk = response_tlv[1].data

    hkdf_inst = hkdf.Hkdf('Pair-Setup-Accessory-Sign-Salt'.encode(),
                          SrpClient.to_byte_array(srp_client.get_session_key()),
                          hash=hashlib.sha512)
    accessory_x = hkdf_inst.expand('Pair-Setup-Accessory-Sign-Info'.encode(), 32)

    accessory_info = accessory_x + accessory_pairing_id + accessory_ltpk

    e25519s = ed25519.VerifyingKey(bytes(response_tlv[1].data))
    try:
        e25519s.verify(bytes(accessory_sig), bytes(accessory_info))
    except AssertionError:
        raise InvalidSignatureError('step #7')

    return {
        'AccessoryPairingID': response_tlv[0].data.decode(),
        'AccessoryLTPK': hexlify(response_tlv[1].data).decode(),
        'iOSPairingId': ios_pairing_id,
        'iOSDeviceLTSK': ios_device_ltsk.to_ascii(encoding='hex').decode()[:64],
        'iOSDeviceLTPK': hexlify(ios_device_ltpk.to_bytes()).decode()
    }


def get_session_keys(pairing_data):
    """
    HomeKit Controller state machine to perform a pair verify operation as described in chapter 4.8 page 47 ff.
    :param pairing_data: the paring data as returned by perform_pair_setup
    :return: tuple of the session keys (controller_to_accessory_key and  accessory_to_controller_key)
    :raises InvalidAuthTagError: if the auth tag could not be verified,
    :raises IncorrectPairingIdError: if the accessory's LTPK could not be found
    :raises InvalidSignatureError: if the accessory's signature could not be verified
    :raises AuthenticationError: if the secured session could not be established
    """

    #
    # Step #1 ios --> accessory (send verify start Request) (page 47)
    #
    ios_key = x25519.X25519PrivateKey.generate()
    ios_key_pub = ios_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )

    request_tlv = [
        tlv8.Entry(Types.kTLVType_State, Steps.M1),
        tlv8.Entry(Types.kTLVType_PublicKey, ios_key_pub)
    ]

    step2_expectations = {
        Types.kTLVType_State: tlv8.DataType.INTEGER,
        Types.kTLVType_PublicKey: tlv8.DataType.BYTES,
        Types.kTLVType_EncryptedData: tlv8.DataType.BYTES
    }
    response_tlv = yield (request_tlv, step2_expectations)

    #
    # Step #3 ios --> accessory (send SRP verify request)  (page 49)
    #
    # response_tlv = TLV.reorder(response_tlv, step2_expectations)
    assert response_tlv[0].type_id == Types.kTLVType_State and response_tlv[0].data == Steps.M2, \
        'get_session_keys: not M2'
    assert response_tlv[1].type_id == Types.kTLVType_PublicKey, 'get_session_keys: no public key'
    assert response_tlv[2].type_id == Types.kTLVType_EncryptedData, 'get_session_keys: no encrypted data'

    # 1) generate shared secret
    accessorys_session_pub_key_bytes = bytes(response_tlv[1].data)
    accessorys_session_pub_key = x25519.X25519PublicKey.from_public_bytes(
        accessorys_session_pub_key_bytes
    )
    shared_secret = ios_key.exchange(accessorys_session_pub_key)

    # 2) derive session key
    hkdf_inst = hkdf.Hkdf('Pair-Verify-Encrypt-Salt'.encode(), shared_secret, hash=hashlib.sha512)
    session_key = hkdf_inst.expand('Pair-Verify-Encrypt-Info'.encode(), 32)

    # 3) verify auth tag on encrypted data and 4) decrypt
    encrypted = response_tlv[2].data
    decrypted = chacha20_aead_decrypt(bytes(), session_key, 'PV-Msg02'.encode(), bytes([0, 0, 0, 0]),
                                      encrypted)
    if type(decrypted) == bool and not decrypted:
        raise InvalidAuthTagError('step 3')
    d1 = tlv8.decode(bytes(decrypted), {
        Types.kTLVType_Identifier: tlv8.DataType.BYTES,
        Types.kTLVType_Signature: tlv8.DataType.BYTES
    })
    # d1 = TLV.reorder(d1, [Types.kTLVType_Identifier, Types.kTLVType_Signature])
    assert d1[0].type_id == Types.kTLVType_Identifier, 'get_session_keys: no identifier'
    assert d1[1].type_id == Types.kTLVType_Signature, 'get_session_keys: no signature'

    # 5) look up pairing by accessory name
    accessory_name = d1[0].data.decode()

    if pairing_data['AccessoryPairingID'] != accessory_name:
        raise IncorrectPairingIdError('step 3')

    accessory_ltpk = ed25519.VerifyingKey(bytes.fromhex(pairing_data['AccessoryLTPK']))

    # 6) verify accessory's signature
    accessory_sig = d1[1].data
    accessory_session_pub_key_bytes = response_tlv[1].data
    accessory_info = accessory_session_pub_key_bytes + accessory_name.encode() + ios_key_pub
    try:
        accessory_ltpk.verify(bytes(accessory_sig), bytes(accessory_info))
    except ed25519.BadSignatureError:
        raise InvalidSignatureError('step 3')

    # 7) create iOSDeviceInfo
    ios_device_info = ios_key_pub + pairing_data['iOSPairingId'].encode() + accessorys_session_pub_key_bytes

    # 8) sign iOSDeviceInfo with long term secret key
    ios_device_ltsk_h = pairing_data['iOSDeviceLTSK']
    ios_device_ltpk_h = pairing_data['iOSDeviceLTPK']
    ios_device_ltsk = ed25519.SigningKey(bytes.fromhex(ios_device_ltsk_h) + bytes.fromhex(ios_device_ltpk_h))
    ios_device_signature = ios_device_ltsk.sign(ios_device_info)

    # 9) construct sub tlv
    sub_tlv = tlv8.encode([
        tlv8.Entry(Types.kTLVType_Identifier, pairing_data['iOSPairingId'].encode()),
        tlv8.Entry(Types.kTLVType_Signature, ios_device_signature)
    ])

    # 10) encrypt and sign
    encrypted_data_with_auth_tag = chacha20_aead_encrypt(bytes(), session_key, 'PV-Msg03'.encode(), bytes([0, 0, 0, 0]),
                                                         sub_tlv)
    tmp = bytearray(encrypted_data_with_auth_tag[0])
    tmp += encrypted_data_with_auth_tag[1]

    # 11) create tlv
    request_tlv = [
        tlv8.Entry(Types.kTLVType_State, Steps.M3),
        tlv8.Entry(Types.kTLVType_EncryptedData, tmp)
    ]

    step3_expectations = {
        Types.kTLVType_State: tlv8.DataType.INTEGER,
        Types.kTLVType_Error: tlv8.DataType.INTEGER
    }
    response_tlv = yield (request_tlv, step3_expectations)

    #
    #   Post Step #4 verification (page 51)
    #
    # response_tlv = TLV.reorder(response_tlv, step3_expectations)
    assert response_tlv[0].type_id == Types.kTLVType_State and response_tlv[0].data == Steps.M4, \
        'get_session_keys: not M4'
    if len(response_tlv) == 2 and response_tlv[1].type_id == Types.kTLVType_Error:
        error_handler(response_tlv[1].data, 'verification')

    # calculate session keys
    hkdf_inst = hkdf.Hkdf('Control-Salt'.encode(), shared_secret, hash=hashlib.sha512)
    controller_to_accessory_key = hkdf_inst.expand('Control-Write-Encryption-Key'.encode(), 32)

    hkdf_inst = hkdf.Hkdf('Control-Salt'.encode(), shared_secret, hash=hashlib.sha512)
    accessory_to_controller_key = hkdf_inst.expand('Control-Read-Encryption-Key'.encode(), 32)

    return controller_to_accessory_key, accessory_to_controller_key
