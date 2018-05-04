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

from homekit import find_device_ip_and_port, HapStatusCodes, HomeKitHTTPConnection


def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit identify app - performs identify on given HomeKit device')
    parser.add_argument('-d', action='store', required=True, dest='device')
    return parser.parse_args()


if __name__ == '__main__':
    args = setup_args_parser()

    connection_data = find_device_ip_and_port(args.device)

    conn = HomeKitHTTPConnection(connection_data['ip'], port=connection_data['port'])

    conn.request('POST', '/identify')

    resp = conn.getresponse()
    if resp.code == 400:
        data = json.loads(resp.read().decode())
        code = data['status']
        print('identify failed because: {reason} ({code}). Is it paired?'.format(reason=HapStatusCodes[code], code=code))
    elif resp.code == 200:
        print('identify succeeded.')
    conn.close()
