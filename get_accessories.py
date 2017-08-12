#!/usr/bin/env python3

import json
import argparse
import http.client
import sys

from homekit import find_device_ip_and_port, SecureHttp, load_pairing, get_session_keys, CharacteristicsTypes, \
    ServicesTypes


def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit perform app - performs operations on paired devices')
    parser.add_argument('-f', action='store', required=True, dest='file', help='File with the pairing data')
    parser.add_argument('-o', action='store', dest='output', default='compact', choices=['json', 'compact'], help='Specify output format')
    return parser


if __name__ == '__main__':
    parser = setup_args_parser()
    args = parser.parse_args()

    pairing_data = load_pairing(args.file)
    if pairing_data is None:
        print('File {file} not found!'.format(file=args.file))
        sys.exit(-1)

    deviceId = pairing_data['AccessoryPairingID']

    connection_data = find_device_ip_and_port(deviceId)
    if connection_data is None:
        print('Device {id} not found!'.format(id=deviceId))
        sys.exit(-1)

    conn = http.client.HTTPConnection(connection_data['ip'], port=connection_data['port'])

    controllerToAccessoryKey, accessoryToControllerKey = get_session_keys(conn, pairing_data)

    sec_http = SecureHttp(conn.sock, accessoryToControllerKey, controllerToAccessoryKey)
    response = sec_http.get('/accessories')
    data = json.loads(response.read().decode())

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
