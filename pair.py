#!/usr/bin/env python3

import argparse
import http.client
import uuid
import sys

from homekit import find_device_ip_and_port, save_pairing, perform_pair_setup


def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit pairing app')
    parser.add_argument('-d', action='store', required=True, dest='device')
    parser.add_argument('-p', action='store', required=True, dest='pin')
    parser.add_argument('-f', action='store', required=True, dest='file')
    return parser.parse_args()


iOSPairingId = str(uuid.uuid4())

if __name__ == '__main__':
    args = setup_args_parser()

    connection_data = find_device_ip_and_port(args.device)
    if connection_data is None:
        print('Device {id} not found'.format(id=args.device))
        sys.exit(-1)

    conn = http.client.HTTPConnection(connection_data['ip'], port=connection_data['port'])

    pairing = perform_pair_setup(conn, args.pin, iOSPairingId)

    save_pairing(args.file, pairing)
