#!/usr/bin/env python3

import json
import argparse
import http.client
import sys

from homekit import find_device_ip_and_port, SecureHttp, load_pairing, get_session_keys


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

    pairing_data = load_pairing(args.file)
    if pairing_data is None:
        print('File {file} not found!'.format(file=args.file))
        sys.exit(-1)

    deviceId = pairing_data['AccessoryPairingID']

    connection_data = find_device_ip_and_port(deviceId)
    if connection_data is None:
        print('Device {id} not found'.format(id=deviceId))
        sys.exit(-1)

    conn = http.client.HTTPConnection(connection_data['ip'], port=connection_data['port'])

    controllerToAccessoryKey, accessoryToControllerKey = get_session_keys(conn, pairing_data)

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
