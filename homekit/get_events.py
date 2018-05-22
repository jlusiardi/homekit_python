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
    parser = argparse.ArgumentParser(description='HomeKit get_events app - listens to events from accessories')
    parser.add_argument('-f', action='store', required=True, dest='file', help='File with the pairing data')
    parser.add_argument('-c', action='append', required=False, dest='characteristics',
                        help='Use aid.iid value to change the value. Repeat to change multiple characteristics.')

    return parser


if __name__ == '__main__':
    parser = setup_args_parser()
    args = parser.parse_args()

    if not args.characteristics:
        parser.print_help()
        sys.exit(-1)

    conn, controllerToAccessoryKey, accessoryToControllerKey = create_session(args.file)
    sec_http = SecureHttp(conn.sock, accessoryToControllerKey, controllerToAccessoryKey)

    characteristics_set = set()
    characteristics = []
    for characteristic in args.characteristics:
        tmp = characteristic.split('.')
        aid = int(tmp[0])
        iid = int(tmp[1])
        characteristics_set.add('{a}.{i}'.format(a=aid, i=iid))
        characteristics.append({'aid': aid, 'iid': iid, 'ev': True})

    body = json.dumps({'characteristics': characteristics})
    response = sec_http.put('/characteristics', body)
    data = response.read().decode()
    if response.code != 204:
        data = json.loads(data)
        for characteristic in data['characteristics']:
            status = characteristic['status']
            if status == 0:
                continue
            aid = characteristic['aid']
            iid = characteristic['iid']
            characteristics_set.remove('{a}.{i}'.format(a=aid, i=iid))
            print('register failed on {aid}.{iid} because: {reason} ({code})'.
                  format(aid=aid, iid=iid, reason=HapStatusCodes[status], code=status))

    print('waiting on events for {chars}'.format(chars=', '.join(characteristics_set)))
    while True:
        r = sec_http.handle_event_response()
        r = json.loads(r)
        for c in r['characteristics']:
            print('event for {aid}.{iid}: {event}'.format(aid=c['aid'], iid=c['iid'], event=c['value']))

    conn.close()
