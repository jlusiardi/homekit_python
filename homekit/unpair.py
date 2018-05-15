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
import os

from homekit import create_session, SecureHttp, load_pairing
from homekit.tlv import TLV


def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit list pairings app')
    parser.add_argument('-f', action='store', required=True, dest='file', help='File with the pairing data')
    parser.add_argument('-d', action='store_true', dest='delete', help='Delete file with the pairing data')
    return parser.parse_args()


if __name__ == '__main__':
    args = setup_args_parser()

    conn, controllerToAccessoryKey, accessoryToControllerKey = create_session(args.file)
    sec_http = SecureHttp(conn.sock, accessoryToControllerKey, controllerToAccessoryKey)
    pairing_data = load_pairing(args.file)
    pairingId = pairing_data['iOSPairingId']

    request_tlv = TLV.encode_dict({
        TLV.kTLVType_State: TLV.M1,
        TLV.kTLVType_Method: TLV.RemovePairing,
        TLV.kTLVType_Identifier: pairingId.encode()
    })

    response = sec_http.post('/pairings', request_tlv.decode())
    data = response.read()
    data = TLV.decode_bytes_to_list(data)
    if data[0][0] == TLV.kTLVType_State and data[0][1] == TLV.M2:
        print('Pairing removed')
        if args.delete:
            os.remove(args.file)
    else:
        print('Remove pairing failed')
