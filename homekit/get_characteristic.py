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

from homekit import create_session, SecureHttp


def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit perform app - performs operations on paired devices')
    parser.add_argument('-f', action='store', required=True, dest='file', help='File with the pairing data')
    parser.add_argument('-c', action='store', required=True, dest='characteristics',
                        help='Read characteristics, multiple characteristcs can be given as comma separated list')
    parser.add_argument('-m', action='store_true', required=False, dest='meta', help='')
    parser.add_argument('-p', action='store_true', required=False, dest='perms', help='')
    parser.add_argument('-t', action='store_true', required=False, dest='type', help='')
    parser.add_argument('-e', action='store_true', required=False, dest='events', help='')
    return parser


if __name__ == '__main__':
    parser = setup_args_parser()
    args = parser.parse_args()

    conn, controllerToAccessoryKey, accessoryToControllerKey = create_session(args.file)

    sec_http = SecureHttp(conn.sock, accessoryToControllerKey, controllerToAccessoryKey)

    # create URL
    url = '/characteristics?id=' + args.characteristics
    if args.meta:
        url += '&meta=1'
    if args.perms:
        url += '&perms=1'
    if args.type:
        url += '&type=1'
    if args.events:
        url += '&ev=1'
    response = sec_http.get(url)

    data = json.loads(response.read().decode())
    print(json.dumps(data, indent=4))

    conn.close()
