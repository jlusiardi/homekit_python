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

import hashlib
import ed25519
import hkdf
import py25519
from binascii import hexlify
from homekit.protocol.tlv import TLV
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
    if error == TLV.kTLVError_Unavailable:
        raise UnavailableError(stage)
    elif error == TLV.kTLVError_Authentication:
        raise AuthenticationError(stage)
    elif error == TLV.kTLVError_Backoff:
        raise BackoffError(stage)
    elif error == TLV.kTLVError_MaxPeers:
        raise MaxPeersError(stage)
    elif error == TLV.kTLVError_MaxTries:
        raise MaxTriesError(stage)
    elif error == TLV.kTLVError_Busy:
        raise BusyError(stage)
    else:
        raise InvalidError(stage)


def perform_pair_setup(connection, pin, ios_pairing_id):
    """
    Performs a pair setup operation as described in chapter 4.7 page 39 ff.

    :param connection: the http_impl connection to the target accessory
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
    headers = {
        'Content-Type': 'application/pairing+tlv8'
    }

    #
    # Step #1 ios --> accessory (send SRP start Request) (see page 39)
    #
    request_tlv = TLV.encode_list([
        (TLV.kTLVType_State, TLV.M1),
        (TLV.kTLVType_Method, TLV.PairSetup)
    ])

    connection.request('POST', '/pair-setup', request_tlv, headers)
    resp = connection.getresponse()
    response_tlv = TLV.decode_bytes(resp.read())

    #
    # Step #3 ios --> accessory (send SRP verify request) (see page 41)
    #
    response_tlv = TLV.reorder(response_tlv,
                               [TLV.kTLVType_State, TLV.kTLVType_Error, TLV.kTLVType_PublicKey, TLV.kTLVType_Salt])
    assert response_tlv[0][0] == TLV.kTLVType_State and response_tlv[0][1] == TLV.M2, 'perform_pair_setup: State not M2'

    # the errors here can be:
    #  * kTLVError_Unavailable: Device is paired
    #  * kTLVError_MaxTries: More than 100 unsuccessfull attempts
    #  * kTLVError_Busy: There is already a pairing going on
    if response_tlv[1][0] == TLV.kTLVType_Error:
        error_handler(response_tlv[1][1], 'step 3')

    assert response_tlv[1][0] == TLV.kTLVType_PublicKey, 'perform_pair_setup: Not a public key'
    assert response_tlv[2][0] == TLV.kTLVType_Salt, 'perform_pair_setup: Not a salt'

    srp_client = SrpClient('Pair-Setup', pin)
    srp_client.set_salt(response_tlv[2][1])
    srp_client.set_server_public_key(response_tlv[1][1])
    client_pub_key = srp_client.get_public_key()
    client_proof = srp_client.get_proof()

    response_tlv = TLV.encode_list([
        (TLV.kTLVType_State, TLV.M3),
        (TLV.kTLVType_PublicKey, SrpClient.to_byte_array(client_pub_key)),
        (TLV.kTLVType_Proof, SrpClient.to_byte_array(client_proof)),
    ])

    connection.request('POST', '/pair-setup', response_tlv, headers)
    resp = connection.getresponse()
    response_tlv = TLV.decode_bytes(resp.read())

    #
    # Step #5 ios --> accessory (Exchange Request) (see page 43)
    #

    # M4 Verification (page 43)
    response_tlv = TLV.reorder(response_tlv, [TLV.kTLVType_State, TLV.kTLVType_Error, TLV.kTLVType_Proof])
    assert response_tlv[0][0] == TLV.kTLVType_State and response_tlv[0][1] == TLV.M4, \
        'perform_pair_setup: State not M4'
    if response_tlv[1][0] == TLV.kTLVType_Error:
        error_handler(response_tlv[1][1], 'step 5')

    assert response_tlv[1][0] == TLV.kTLVType_Proof, 'perform_pair_setup: Not a proof'
    if not srp_client.verify_servers_proof(response_tlv[1][1]):
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
        (TLV.kTLVType_Identifier, ios_device_pairing_id),
        (TLV.kTLVType_PublicKey, ios_device_ltpk.to_bytes()),
        (TLV.kTLVType_Signature, ios_device_signature)
    ]
    sub_tlv_b = TLV.encode_list(sub_tlv)

    # taking tge iOSDeviceX as key was reversed from
    # https://github.com/KhaosT/HAP-NodeJS/blob/2ea9d761d9bd7593dd1949fec621ab085af5e567/lib/HAPServer.js
    # function handlePairStepFive calling encryption.encryptAndSeal
    encrypted_data_with_auth_tag = chacha20_aead_encrypt(bytes(), session_key, 'PS-Msg05'.encode(), bytes([0, 0, 0, 0]),
                                                         sub_tlv_b)
    tmp = bytearray(encrypted_data_with_auth_tag[0])
    tmp += encrypted_data_with_auth_tag[1]

    response_tlv = [
        (TLV.kTLVType_State, TLV.M5),
        (TLV.kTLVType_EncryptedData, tmp)
    ]
    body = TLV.encode_list(response_tlv)

    connection.request('POST', '/pair-setup', body, headers)
    resp = connection.getresponse()
    response_tlv = TLV.decode_bytes(resp.read())

    #
    # Step #7 ios (Verification) (page 47)
    #
    response_tlv = TLV.reorder(response_tlv, [TLV.kTLVType_State, TLV.kTLVType_Error, TLV.kTLVType_EncryptedData])
    assert response_tlv[0][0] == TLV.kTLVType_State and response_tlv[0][1] == TLV.M6, 'perform_pair_setup: State not M6'
    if response_tlv[1][0] == TLV.kTLVType_Error:
        error_handler(response_tlv[1][1], 'step 7')

    assert response_tlv[1][0] == TLV.kTLVType_EncryptedData, 'perform_pair_setup: No encrypted data'
    decrypted_data = chacha20_aead_decrypt(bytes(), session_key, 'PS-Msg06'.encode(), bytes([0, 0, 0, 0]),
                                           response_tlv[1][1])
    if decrypted_data is False:
        raise homekit.exception.IllegalData('step 7')

    response_tlv = TLV.decode_bytearray(decrypted_data)
    response_tlv = TLV.reorder(response_tlv, [TLV.kTLVType_Identifier, TLV.kTLVType_PublicKey, TLV.kTLVType_Signature])

    assert response_tlv[2][0] == TLV.kTLVType_Signature, 'perform_pair_setup: No signature'
    accessory_sig = response_tlv[2][1]

    assert response_tlv[0][0] == TLV.kTLVType_Identifier, 'perform_pair_setup: No identifier'
    accessory_pairing_id = response_tlv[0][1]

    assert response_tlv[1][0] == TLV.kTLVType_PublicKey, 'perform_pair_setup: No public key'
    accessory_ltpk = response_tlv[1][1]

    hkdf_inst = hkdf.Hkdf('Pair-Setup-Accessory-Sign-Salt'.encode(),
                          SrpClient.to_byte_array(srp_client.get_session_key()),
                          hash=hashlib.sha512)
    accessory_x = hkdf_inst.expand('Pair-Setup-Accessory-Sign-Info'.encode(), 32)

    accessory_info = accessory_x + accessory_pairing_id + accessory_ltpk

    e25519s = ed25519.VerifyingKey(bytes(response_tlv[1][1]))
    try:
        e25519s.verify(bytes(accessory_sig), bytes(accessory_info))
    except AssertionError:
        raise InvalidSignatureError('step #7')

    return {
        'AccessoryPairingID': response_tlv[0][1].decode(),
        'AccessoryLTPK': hexlify(response_tlv[1][1]).decode(),
        'iOSPairingId': ios_pairing_id,
        'iOSDeviceLTSK': ios_device_ltsk.to_ascii(encoding='hex').decode(),
        'iOSDeviceLTPK': hexlify(ios_device_ltpk.to_bytes()).decode()
    }


def get_session_keys(conn, pairing_data):
    """
    HomeKit Controller side call to perform a pair verify operation as described in chapter 4.8 page 47 ff.

    :param conn: the http_impl connection to the target accessory
    :param pairing_data: the paring data as returned by perform_pair_setup
    :return: tuple of the session keys (controller_to_accessory_key and  accessory_to_controller_key)
    :raises InvalidAuthTagError: if the auth tag could not be verified,
    :raises IncorrectPairingIdError: if the accessory's LTPK could not be found
    :raises InvalidSignatureError: if the accessory's signature could not be verified
    :raises AuthenticationError: if the secured session could not be established
    """
    headers = {
        'Content-Type': 'application/pairing+tlv8'
    }

    #
    # Step #1 ios --> accessory (send verify start Request) (page 47)
    #
    ios_key = py25519.Key25519()

    request_tlv = TLV.encode_list([
        (TLV.kTLVType_State, TLV.M1),
        (TLV.kTLVType_PublicKey, ios_key.pubkey)
    ])

    conn.request('POST', '/pair-verify', request_tlv, headers)
    resp = conn.getresponse()
    response_tlv = TLV.decode_bytes(resp.read())

    #
    # Step #3 ios --> accessory (send SRP verify request)  (page 49)
    #
    response_tlv = TLV.reorder(response_tlv, [TLV.kTLVType_State, TLV.kTLVType_PublicKey, TLV.kTLVType_EncryptedData])
    assert response_tlv[0][0] == TLV.kTLVType_State and response_tlv[0][1] == TLV.M2, 'get_session_keys: not M2'
    assert response_tlv[1][0] == TLV.kTLVType_PublicKey, 'get_session_keys: no public key'
    assert response_tlv[2][0] == TLV.kTLVType_EncryptedData, 'get_session_keys: no encrypted data'

    # 1) generate shared secret
    accessorys_session_pub_key_bytes = response_tlv[1][1]
    shared_secret = ios_key.get_ecdh_key(
        py25519.Key25519(pubkey=bytes(accessorys_session_pub_key_bytes), verifyingkey=bytes()))

    # 2) derive session key
    hkdf_inst = hkdf.Hkdf('Pair-Verify-Encrypt-Salt'.encode(), shared_secret, hash=hashlib.sha512)
    session_key = hkdf_inst.expand('Pair-Verify-Encrypt-Info'.encode(), 32)

    # 3) verify auth tag on encrypted data and 4) decrypt
    encrypted = response_tlv[2][1]
    decrypted = chacha20_aead_decrypt(bytes(), session_key, 'PV-Msg02'.encode(), bytes([0, 0, 0, 0]),
                                      encrypted)
    if type(decrypted) == bool and not decrypted:
        raise InvalidAuthTagError('step 3')
    d1 = TLV.decode_bytes(decrypted)
    d1 = TLV.reorder(d1, [TLV.kTLVType_Identifier, TLV.kTLVType_Signature])
    assert d1[0][0] == TLV.kTLVType_Identifier, 'get_session_keys: no identifier'
    assert d1[1][0] == TLV.kTLVType_Signature, 'get_session_keys: no signature'

    # 5) look up pairing by accessory name
    accessory_name = d1[0][1].decode()

    if pairing_data['AccessoryPairingID'] != accessory_name:
        raise IncorrectPairingIdError('step 3')

    accessory_ltpk = py25519.Key25519(pubkey=bytes(), verifyingkey=bytes.fromhex(pairing_data['AccessoryLTPK']))

    # 6) verify accessory's signature
    accessory_sig = d1[1][1]
    accessory_session_pub_key_bytes = response_tlv[1][1]
    accessory_info = accessory_session_pub_key_bytes + accessory_name.encode() + ios_key.pubkey
    if not accessory_ltpk.verify(bytes(accessory_sig), bytes(accessory_info)):
        raise InvalidSignatureError('step 3')

    # 7) create iOSDeviceInfo
    ios_device_info = ios_key.pubkey + pairing_data['iOSPairingId'].encode() + accessorys_session_pub_key_bytes

    # 8) sign iOSDeviceInfo with long term secret key
    ios_device_ltsk_h = pairing_data['iOSDeviceLTSK']
    ios_device_ltsk = py25519.Key25519(secretkey=bytes.fromhex(ios_device_ltsk_h))
    ios_device_signature = ios_device_ltsk.sign(ios_device_info)

    # 9) construct sub tlv
    sub_tlv = TLV.encode_list([
        (TLV.kTLVType_Identifier, pairing_data['iOSPairingId'].encode()),
        (TLV.kTLVType_Signature, ios_device_signature)
    ])

    # 10) encrypt and sign
    encrypted_data_with_auth_tag = chacha20_aead_encrypt(bytes(), session_key, 'PV-Msg03'.encode(), bytes([0, 0, 0, 0]),
                                                         sub_tlv)
    tmp = bytearray(encrypted_data_with_auth_tag[0])
    tmp += encrypted_data_with_auth_tag[1]

    # 11) create tlv
    request_tlv = TLV.encode_list([
        (TLV.kTLVType_State, TLV.M3),
        (TLV.kTLVType_EncryptedData, tmp)
    ])

    # 12) send to accessory
    conn.request('POST', '/pair-verify', request_tlv, headers)
    resp = conn.getresponse()
    response_tlv = TLV.decode_bytes(resp.read())

    #
    #   Post Step #4 verification (page 51)
    #
    response_tlv = TLV.reorder(response_tlv, [TLV.kTLVType_State, TLV.kTLVType_Error])
    assert response_tlv[0][0] == TLV.kTLVType_State and response_tlv[0][1] == TLV.M4, 'get_session_keys: not M4'
    if len(response_tlv) == 2 and response_tlv[1][0] == TLV.kTLVType_Error:
        error_handler(response_tlv[1][1] , 'verification')

    # calculate session keys
    hkdf_inst = hkdf.Hkdf('Control-Salt'.encode(), shared_secret, hash=hashlib.sha512)
    controller_to_accessory_key = hkdf_inst.expand('Control-Write-Encryption-Key'.encode(), 32)

    hkdf_inst = hkdf.Hkdf('Control-Salt'.encode(), shared_secret, hash=hashlib.sha512)
    accessory_to_controller_key = hkdf_inst.expand('Control-Read-Encryption-Key'.encode(), 32)

    return controller_to_accessory_key, accessory_to_controller_key
