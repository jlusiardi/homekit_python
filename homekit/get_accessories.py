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

from homekit import SecureHttp, load_pairing, CharacteristicsTypes, ServicesTypes, save_pairing, create_session

  
def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit perform app - performs operations on paired devices')
    parser.add_argument('-f', action='store', required=True, dest='file', help='File with the pairing data')
    parser.add_argument('-o', action='store', dest='output', default='compact', choices=['json', 'compact'], help='Specify output format')
    return parser


if __name__ == '__main__':
    parser = setup_args_parser()
    args = parser.parse_args()

    conn, controllerToAccessoryKey, accessoryToControllerKey = create_session(args.file)

    sec_http = SecureHttp(conn.sock, accessoryToControllerKey, controllerToAccessoryKey)
    response = sec_http.get('/accessories')
    data = json.loads(response.read().decode())

    # save accessories data to pairing file
    pairing_data = load_pairing(args.file)
    pairing_data['accessories'] = data['accessories']
    save_pairing(args.file, pairing_data)

    if args.output == 'json':
        print(json.dumps(data, indent=4))

    if args.output == 'compact':
        for accessory in data['accessories']:
            aid = accessory['aid']
            for service in accessory['services']:
                s_type = service['type']
                s_iid = service['iid']
                print('{aid}.{iid}: >{stype}<'.format(aid=aid, iid=s_iid, stype=ServicesTypes.get_short(s_type)))

                for characteristic in service['characteristics']:
                    c_iid = characteristic['iid']
                    value = characteristic.get('value', '')
                    c_type = characteristic['type']
                    perms = ','.join(characteristic['perms'])
                    desc = characteristic.get('description', '')

                    print('  {aid}.{iid}: {value} ({description}) >{ctype}< [{perms}]'.format(aid=aid, iid=c_iid, value=value,
                                                                              ctype=CharacteristicsTypes.get_short(c_type),
                                                                              perms=perms, description = desc))

    conn.close()
