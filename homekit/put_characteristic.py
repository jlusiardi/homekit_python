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

from homekit import SecureHttp, load_pairing, HapStatusCodes, save_pairing, create_session


def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit perform app - performs operations on paired devices')
    parser.add_argument('-f', action='store', required=True, dest='file', help='File with the pairing data')
    parser.add_argument('-c', action='store', required=False, dest='characteristics')
    parser.add_argument('-v', action='store', required=False, dest='value')

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

    if not args.characteristics:
        parser.print_help()
        sys.exit(-1)
    if not args.value:
        parser.print_help()
        sys.exit(-1)

    tmp = args.characteristics.split('.')
    aid = int(tmp[0])
    iid = int(tmp[1])
    value = args.value

    conn, controllerToAccessoryKey, accessoryToControllerKey = create_session(args.file)
    sec_http = SecureHttp(conn.sock, accessoryToControllerKey, controllerToAccessoryKey)

    pairing_data = load_pairing(args.file)
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
    if characteristic_type == 'bool':
        try:
            value = strtobool(value)
        except ValueError:
            print('{v} is no valid boolean!'.format(v=value))
            sys.exit(-1)

    # TODO more conversion according to Table 5-5 page 67 required
    else:
        pass

    body = json.dumps({'characteristics': [{'aid': aid, 'iid': iid, 'value': value}]})
    response = sec_http.put('/characteristics', body)
    data = response.read().decode()
    if response.code != 204:
        data = json.loads(data)
        code = data['characteristics'][0]['status']
        print('put_characteristics failed because: {reason} ({code})'.format(reason=HapStatusCodes[code], code=code))
    else:
        print('put_characteristics succeeded')

    conn.close()
