#!/usr/bin/env python3

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

import argparse

from homekit import create_session, SecureHttp, load_pairing
from homekit.tlv import TLV


def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit list pairings app')
    parser.add_argument('-f', action='store', required=True, dest='file', help='File with the pairing data')
    return parser.parse_args()


if __name__ == '__main__':
    args = setup_args_parser()

    conn, controllerToAccessoryKey, accessoryToControllerKey = create_session(args.file)
    sec_http = SecureHttp(conn.sock, accessoryToControllerKey, controllerToAccessoryKey)

    request_tlv = TLV.encode_dict({
        TLV.kTLVType_State: TLV.M1,
        TLV.kTLVType_Method: TLV.ListPairings
    })

    response = sec_http.post('/pairings', request_tlv.decode())
    data = response.read()
    data = TLV.decode_bytes_to_list(data)

    if not (data[0][0] == TLV.kTLVType_State and data[0][1] == TLV.M2):
        print('Illegal reply.')
    elif data[1][0] == TLV.kTLVType_Error and data[1][1] == TLV.kTLVError_Authentication:
        print('Device not paired.')
    else:
        for d in data[1:]:
            if d[0] == TLV.kTLVType_Identifier:
                print('Pairing Id: {id}'.format(id=d[1].decode()))
            if d[0] == TLV.kTLVType_PublicKey:
                print('\tPublic Key: 0x{key}'.format(key=d[1].hex()))
            if d[0] == TLV.kTLVType_Permissions:
                user_type = 'regular user'
                if d[1] == b'\x01':
                    user_type = 'admin user'
                print('\tPermissions: {perm} ({type})'.format(perm=int.from_bytes(d[1], byteorder='little'),
                                                              type=user_type))
