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

import sys
import hkdf
import hashlib
import ed25519
import py25519
import homekit.exception
from binascii import hexlify
from homekit.tlv import TLV
from homekit.srp import SrpClient
from homekit.chacha20poly1305 import chacha20_aead_decrypt, chacha20_aead_encrypt


def error_handler(error, stage):
    if error == TLV.kTLVError_Unavailable:
        raise homekit.exception.UnavailableError(stage)
    elif error == TLV.kTLVError_Authentication:
        raise homekit.exception.AuthenticationError(stage)
    elif error == TLV.kTLVError_Backoff:
        raise homekit.exception.BackoffError(stage)
    elif error == TLV.kTLVError_MaxPeers:
        raise homekit.exception.MaxPeersError(stage)
    elif error == TLV.kTLVError_MaxTries:
        raise homekit.exception.MaxTriesError(stage)
    elif error == TLV.kTLVError_Unavailable:
        raise homekit.exception.UnavailableError(stage)
    elif error == TLV.kTLVError_Busy:
        raise homekit.exception.BusyError(stage)
    else:
        raise homekit.exception.InvalidError(stage)


def perform_pair_setup(connection, pin, ios_pairing_id):
    """
    Performs a pair setup operation as described in chapter 4.7 page 39 ff.

    :param connection: the http connection to the target accessory
    :param pin: the setup code from the accessory
    :param ios_pairing_id: the id of the simulated ios device
    :return: a dict with the ios device's part of the pairing information
    """
    headers = {
        'Content-Type': 'application/pairing+tlv8'
    }

    #
    # Step #1 ios --> accessory (send SRP start Request) (see page 39)
    #
    request_tlv = TLV.encode_dict({
        TLV.kTLVType_State: TLV.M1,
        TLV.kTLVType_Method: TLV.PairSetup
    })

    connection.request('POST', '/pair-setup', request_tlv, headers)
    resp = connection.getresponse()
    response_tlv = TLV.decode_bytes(resp.read())

    #
    # Step #3 ios --> accessory (send SRP verify request) (see page 41)
    #
    assert TLV.kTLVType_State in response_tlv, response_tlv
    assert response_tlv[TLV.kTLVType_State] == TLV.M2
    if TLV.kTLVType_Error in response_tlv:
        error_handler(response_tlv[TLV.kTLVType_Error], "step 3")

    srp_client = SrpClient('Pair-Setup', pin)
    srp_client.set_salt(response_tlv[TLV.kTLVType_Salt])
    srp_client.set_server_public_key(response_tlv[TLV.kTLVType_PublicKey])
    client_pub_key = srp_client.get_public_key()
    client_proof = srp_client.get_proof()

    response_tlv = TLV.encode_dict({
        TLV.kTLVType_State: TLV.M3,
        TLV.kTLVType_PublicKey: SrpClient.to_byte_array(client_pub_key),
        TLV.kTLVType_Proof: SrpClient.to_byte_array(client_proof),
    })

    connection.request('POST', '/pair-setup', response_tlv, headers)
    resp = connection.getresponse()
    response_tlv = TLV.decode_bytes(resp.read())

    #
    # Step #5 ios --> accessory (Exchange Request) (see page 43)
    #

    # M4 Verification (page 43)
    assert TLV.kTLVType_State in response_tlv, response_tlv
    assert response_tlv[TLV.kTLVType_State] == TLV.M4
    if TLV.kTLVType_Error in response_tlv:
        error_handler(response_tlv[TLV.kTLVType_Error], "step 5")

    assert TLV.kTLVType_Proof in response_tlv
    if not srp_client.verify_servers_proof(response_tlv[TLV.kTLVType_Proof]):
        print('Step #5: wrong proof!')

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

    sub_tlv = {
        TLV.kTLVType_Identifier: ios_device_pairing_id,
        TLV.kTLVType_PublicKey: ios_device_ltpk.to_bytes(),
        TLV.kTLVType_Signature: ios_device_signature
    }
    sub_tlv_b = TLV.encode_dict(sub_tlv)

    # taking tge iOSDeviceX as key was reversed from
    # https://github.com/KhaosT/HAP-NodeJS/blob/2ea9d761d9bd7593dd1949fec621ab085af5e567/lib/HAPServer.js
    # function handlePairStepFive calling encryption.encryptAndSeal
    encrypted_data_with_auth_tag = chacha20_aead_encrypt(bytes(), session_key, 'PS-Msg05'.encode(), bytes([0, 0, 0, 0]),
                                                         sub_tlv_b)
    tmp = bytearray(encrypted_data_with_auth_tag[0])
    tmp += encrypted_data_with_auth_tag[1]

    response_tlv = {
        TLV.kTLVType_State: TLV.M5,
        TLV.kTLVType_EncryptedData: tmp
    }
    body = TLV.encode_dict(response_tlv)

    connection.request('POST', '/pair-setup', body, headers)
    resp = connection.getresponse()
    response_tlv = TLV.decode_bytes(resp.read())

    #
    # Step #7 ios (Verification) (page 47)
    #
    assert response_tlv[TLV.kTLVType_State] == TLV.M6
    if TLV.kTLVType_Error in response_tlv:
        error_handler(response_tlv[TLV.kTLVType_Error], "step 7")

    assert TLV.kTLVType_EncryptedData in response_tlv
    decrypted_data = chacha20_aead_decrypt(bytes(), session_key, 'PS-Msg06'.encode(), bytes([0, 0, 0, 0]),
                                           response_tlv[TLV.kTLVType_EncryptedData])
    if decrypted_data == False:
        raise homekit.exception.IllegalData("step 7")

    response_tlv = TLV.decode_bytearray(decrypted_data)
    assert TLV.kTLVType_Signature in response_tlv
    accessory_sig = response_tlv[TLV.kTLVType_Signature]

    assert TLV.kTLVType_Identifier in response_tlv
    accessory_pairing_id = response_tlv[TLV.kTLVType_Identifier]

    assert TLV.kTLVType_PublicKey in response_tlv
    accessory_ltpk = response_tlv[TLV.kTLVType_PublicKey]
    hkdf_inst = hkdf.Hkdf('Pair-Setup-Accessory-Sign-Salt'.encode(),
                          SrpClient.to_byte_array(srp_client.get_session_key()),
                          hash=hashlib.sha512)
    accessory_x = hkdf_inst.expand('Pair-Setup-Accessory-Sign-Info'.encode(), 32)

    accessory_info = accessory_x + accessory_pairing_id + accessory_ltpk

    e25519s = ed25519.VerifyingKey(bytes(response_tlv[TLV.kTLVType_PublicKey]))
    e25519s.verify(bytes(accessory_sig), bytes(accessory_info))

    return {
        'AccessoryPairingID': response_tlv[TLV.kTLVType_Identifier].decode(),
        'AccessoryLTPK': hexlify(response_tlv[TLV.kTLVType_PublicKey]).decode(),
        'iOSPairingId': ios_pairing_id,
        'iOSDeviceLTSK': ios_device_ltsk.to_ascii(encoding='hex').decode(),
        'iOSDeviceLTPK': hexlify(ios_device_ltpk.to_bytes()).decode()
    }


def get_session_keys(conn, pairing_data):
    """
    Performs a pair verify operation as described in chapter 4.8 page 47 ff.

    :param conn: the http connection to the target accessory
    :param pairing_data: the paring data as returned by perform_pair_setup
    :return: tuple of the session keys (controller_to_accessory_key and  accessory_to_controller_key)
    """
    headers = {
        'Content-Type': 'application/pairing+tlv8'
    }

    #
    # Step #1 ios --> accessory (send verify start Request) (page 47)
    #
    ios_key = py25519.Key25519()

    request_tlv = TLV.encode_dict({
        TLV.kTLVType_State: TLV.M1,
        TLV.kTLVType_PublicKey: ios_key.pubkey
    })

    conn.request('POST', '/pair-verify', request_tlv, headers)
    resp = conn.getresponse()
    response_tlv = TLV.decode_bytes(resp.read())

    #
    # Step #3 ios --> accessory (send SRP verify request)  (page 49)
    #
    assert TLV.kTLVType_State in response_tlv, response_tlv
    assert response_tlv[TLV.kTLVType_State] == TLV.M2
    assert TLV.kTLVType_PublicKey in response_tlv, response_tlv
    assert TLV.kTLVType_EncryptedData in response_tlv, response_tlv

    # 1) generate shared secret
    accessorys_session_pub_key_bytes = response_tlv[TLV.kTLVType_PublicKey]
    shared_secret = ios_key.get_ecdh_key(
        py25519.Key25519(pubkey=bytes(accessorys_session_pub_key_bytes), verifyingkey=bytes()))

    # 2) derive session key
    hkdf_inst = hkdf.Hkdf('Pair-Verify-Encrypt-Salt'.encode(), shared_secret, hash=hashlib.sha512)
    session_key = hkdf_inst.expand('Pair-Verify-Encrypt-Info'.encode(), 32)

    # 3) verify authtag on encrypted data and 4) decrypt
    encrypted = response_tlv[TLV.kTLVType_EncryptedData]
    decrypted = chacha20_aead_decrypt(bytes(), session_key, 'PV-Msg02'.encode(), bytes([0, 0, 0, 0]),
                                      encrypted)
    if decrypted == False:
        raise homekit.exception.InvalidAuth("step 3")
    d1 = TLV.decode_bytes(decrypted)
    assert TLV.kTLVType_Identifier in d1
    assert TLV.kTLVType_Signature in d1

    # 5) look up pairing by accessory name
    accessory_name = d1[TLV.kTLVType_Identifier].decode()

    if pairing_data['AccessoryPairingID'] != accessory_name:
        raise homekit.exception.IncorrectPairingID("step 3")
        
    accessory_ltpk = py25519.Key25519(pubkey=bytes(), verifyingkey=bytes.fromhex(pairing_data['AccessoryLTPK']))

    # 6) verify accessory's signature
    accessory_sig = d1[TLV.kTLVType_Signature]
    accessory_session_pub_key_bytes = response_tlv[TLV.kTLVType_PublicKey]
    accessory_info = accessory_session_pub_key_bytes + accessory_name.encode() + ios_key.pubkey
    if not accessory_ltpk.verify(bytes(accessory_sig), bytes(accessory_info)):
        raise homekit.exception.InvalidSignature("step 3")

    # 7) create iOSDeviceInfo
    ios_device_info = ios_key.pubkey + pairing_data['iOSPairingId'].encode() + accessorys_session_pub_key_bytes

    # 8) sign iOSDeviceInfo with long term secret key
    ios_device_ltsk_h = pairing_data['iOSDeviceLTSK']
    ios_device_ltsk = py25519.Key25519(secretkey=bytes.fromhex(ios_device_ltsk_h))
    ios_device_signature = ios_device_ltsk.sign(ios_device_info)

    # 9) construct sub tlv
    sub_tlv = TLV.encode_dict({
        TLV.kTLVType_Identifier: pairing_data['iOSPairingId'].encode(),
        TLV.kTLVType_Signature: ios_device_signature
    })

    # 10) encrypt and sign
    encrypted_data_with_auth_tag = chacha20_aead_encrypt(bytes(), session_key, 'PV-Msg03'.encode(), bytes([0, 0, 0, 0]),
                                                         sub_tlv)
    tmp = bytearray(encrypted_data_with_auth_tag[0])
    tmp += encrypted_data_with_auth_tag[1]

    # 11) create tlv
    request_tlv = TLV.encode_dict({
        TLV.kTLVType_State: TLV.M3,
        TLV.kTLVType_EncryptedData: tmp
    })

    # 12) send to accessory
    conn.request('POST', '/pair-verify', request_tlv, headers)
    resp = conn.getresponse()
    response_tlv = TLV.decode_bytes(resp.read())

    #
    #   Post Step #4 verification (page 51)
    #
    if TLV.kTLVType_Error in response_tlv:
        error_handler(response_tlv[TLV.kTLVType_Error], "verification")
    assert TLV.kTLVType_State in response_tlv
    assert response_tlv[TLV.kTLVType_State] == TLV.M4

    # calculate session keys
    hkdf_inst = hkdf.Hkdf('Control-Salt'.encode(), shared_secret, hash=hashlib.sha512)
    controller_to_accessory_key = hkdf_inst.expand('Control-Write-Encryption-Key'.encode(), 32)

    hkdf_inst = hkdf.Hkdf('Control-Salt'.encode(), shared_secret, hash=hashlib.sha512)
    accessory_to_controller_key = hkdf_inst.expand('Control-Read-Encryption-Key'.encode(), 32)

    return controller_to_accessory_key, accessory_to_controller_key
