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
from time import sleep
from homekit.chacha20poly1305 import chacha20_aead_encrypt, chacha20_aead_decrypt


def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit perform app - performs operations on paired devices')
    parser.add_argument('-f', action='store', required=True, dest='file', help='File with the pairing data')
    parser.add_argument('-c', action='store', required=False, dest='characteristics')

    return parser


if __name__ == '__main__':
    parser = setup_args_parser()
    args = parser.parse_args()

    if not args.characteristics:
        parser.print_help()
        sys.exit(-1)

    tmp = args.characteristics.split('.')
    aid = int(tmp[0])
    iid = int(tmp[1])

    conn, controllerToAccessoryKey, accessoryToControllerKey = create_session(args.file)
    sec_http = SecureHttp(conn.sock, accessoryToControllerKey, controllerToAccessoryKey)

    body = json.dumps({'characteristics': [{'aid': aid, 'iid': iid, 'ev': True},{'aid': aid, 'iid': 23, 'ev': True}]})
    response = sec_http.put('/characteristics', body)
    data = response.read().decode()
    if response.code != 204:
        data = json.loads(data)
        code = data['characteristics'][0]['status']
        print('put_characteristics failed because: {reason} ({code})'.format(reason=HapStatusCodes[code], code=code))
    else:
        print('put_characteristics succeeded')
    print(conn.sock)
    while True:
        r = sec_http._handle_response()
        r = json.loads(r)
        for c in r['characteristics']:
            print('event for {aid}.{iid}: {event}'.format(aid=c['aid'], iid=c['iid'], event=c['value']))

    conn.close()
