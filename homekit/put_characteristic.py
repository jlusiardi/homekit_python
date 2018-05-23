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

import json
import argparse
import sys
from distutils.util import strtobool
import base64
import binascii

from homekit import SecureHttp, load_pairing, HapStatusCodes, save_pairing, create_session
from homekit.model.characteristics import CharacteristicFormats
from homekit.tlv import TLV, TlvParseException


def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit put_characteristic app - change values of characteristics ' +
                                                 'on paired HomeKit accessories.')
    parser.add_argument('-f', action='store', required=True, dest='file', help='File with the pairing data')
    parser.add_argument('-c', action='append', required=False, dest='characteristics', nargs=2,
                        help='Use aid.iid value to change the value. Repeat to change multiple characteristics.')

    return parser


def get_format(pairing_data, aid, iid):
    format = None
    for d in pairing_data['accessories']:
        if 'aid' in d and d['aid'] == aid:
            for s in d['services']:
                for c in s['characteristics']:
                    if 'iid' in c and c['iid'] == iid:
                        format = c['format']
    return format


if __name__ == '__main__':
    parser = setup_args_parser()
    args = parser.parse_args()

    if 'characteristics' not in args or not args.characteristics:
        parser.print_help()
        sys.exit(-1)

    conn, controllerToAccessoryKey, accessoryToControllerKey = create_session(args.file)
    sec_http = SecureHttp(conn.sock, accessoryToControllerKey, controllerToAccessoryKey)

    pairing_data = load_pairing(args.file)

    # args.characteristics contains a list of lists like [['1.10', 'on'], ['1.11', '50']]
    characteristics_set = set()
    characteristics = []
    for characteristic in args.characteristics:
        # extract aid, iid and value from cli params
        tmp = characteristic[0].split('.')
        aid = int(tmp[0])
        iid = int(tmp[1])
        value = characteristic[1]

        # first check if the accessories data is in the paring data
        characteristic_type = None
        if 'accessories' not in pairing_data or not get_format(pairing_data, aid, iid):
            # nope, so get it via /accessories and save it
            response = sec_http.get('/accessories')
            data = json.loads(response.read().decode())
            pairing_data['accessories'] = data['accessories']
            save_pairing(args.file, pairing_data)
        # after loading the accessories data the aid.iid should be there...
        characteristic_type = get_format(pairing_data, aid, iid)
        if not characteristic_type:
            print('Characteristic {aid}.{iid} not found'.format(aid=aid, iid=iid))
            sys.exit(-1)

        # reformat the value to fit the required format
        if characteristic_type == CharacteristicFormats.bool:
            try:
                value = strtobool(value)
            except ValueError:
                print('{v} is no valid boolean!'.format(v=value))
                sys.exit(-1)
        if characteristic_type in [CharacteristicFormats.uint64, CharacteristicFormats.uint32,
                                   CharacteristicFormats.uint16, CharacteristicFormats.uint8,
                                   CharacteristicFormats.int]:
            try:
                value = int(value)
            except ValueError:
                print('{v} is no valid int!'.format(v=value))
                sys.exit(-1)
        if characteristic_type == CharacteristicFormats.float:
            try:
                value = float(value)
            except ValueError:
                print('{v} is no valid float!'.format(v=value))
                sys.exit(-1)
        if characteristic_type == CharacteristicFormats.data:
            try:
                base64.decodebytes(value.encode())
            except binascii.Error:
                print('{v} is no valid base64 encoded data!'.format(v=value))
                sys.exit(-1)
        if characteristic_type == CharacteristicFormats.tlv8:
            try:
                b = base64.decodebytes(value.encode())
                tlv = TLV.decode_bytes(b)
            except (binascii.Error, TlvParseException):
                print('{v} is no valid base64 encoded tlv!'.format(v=value))
                sys.exit(-1)

        # Nothing to do for CharacteristicFormats.string!

        characteristics.append({'aid': aid, 'iid': iid, 'value': value})
        characteristics_set.add('{a}.{i}'.format(a=aid, i=iid))

    body = json.dumps({'characteristics': characteristics})
    response = sec_http.put('/characteristics', body)
    if response.code != 204:
        data = response.read().decode()
        data = json.loads(data)
        for characteristic in data['characteristics']:
            status = characteristic['status']
            if status == 0:
                continue
            aid = characteristic['aid']
            iid = characteristic['iid']
            characteristics_set.remove('{a}.{i}'.format(a=aid, i=iid))
            print('put_characteristics failed on {aid}.{iid} because: {reason} ({code})'.
                  format(aid=aid, iid=iid, reason=HapStatusCodes[status], code=status))
    if len(characteristics_set):
        print('put_characteristics succeeded for {chars}'.format(chars=', '.join(characteristics_set)))

    conn.close()
