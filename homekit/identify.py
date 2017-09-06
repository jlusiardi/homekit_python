#!/usr/bin/env python3

import json
import argparse
import http.client

from homekit import find_device_ip_and_port, HapStatusCodes


def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit identify app - performs identify on given HomeKit device')
    parser.add_argument('-d', action='store', required=True, dest='device')
    return parser.parse_args()


if __name__ == '__main__':
    args = setup_args_parser()

    connection_data = find_device_ip_and_port(args.device)

    conn = http.client.HTTPConnection(connection_data['ip'], port=connection_data['port'])

    conn.request('POST', '/identify')

    resp = conn.getresponse()
    if resp.code == 400:
        data = json.loads(resp.read().decode())
        code = data['status']
        print('identify failed because: {reason} ({code}). Is it paired?'.format(reason=HapStatusCodes[code], code=code))
    elif resp.code == 200:
        print('identify succeeded.')
    conn.close()
