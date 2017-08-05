import json
import argparse
import http.client
import sys

from homekit import find_device_ip_and_port, SecureHttp, load_pairing, get_session_keys, StatusCodes


def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit perform app - performs operations on paired devices')
    parser.add_argument('-d', action='store', required=True, dest='device')
    parser.add_argument('-f', action='store', required=True, dest='file')
    parser.add_argument('-o', action='store', required=True, dest='operation',
                        choices=['list_pairings', 'remove_pairing', 'add_pairing', 'get_accessories',
                                 'get_characteristics', 'put_characteristics'])

    parser.add_argument('-c', action='store', required=False, dest='characteristics')
    parser.add_argument('-v', action='store', required=False, dest='value')

    return parser


if __name__ == '__main__':
    parser = setup_args_parser()
    args = parser.parse_args()

    connection_data = find_device_ip_and_port(args.device)
    if connection_data is None:
        print('Device not found')
        sys.exit(-1)

    conn = http.client.HTTPConnection(connection_data['ip'], port=connection_data['port'])
    pairing_data = load_pairing(args.file)

    controllerToAccessoryKey, accessoryToControllerKey = get_session_keys(conn, pairing_data)

    if args.operation == 'list_pairings':
        pass
    elif args.operation == 'remove_pairing':
        pass
    elif args.operation == 'add_pairing':
        pass
    elif args.operation == 'put_characteristics':
        if not args.characteristics:
            parser.print_help()
            sys.exit(-1)
        if not args.value:
            parser.print_help()
            sys.exit(-1)

        sec_http = SecureHttp(conn.sock, accessoryToControllerKey, controllerToAccessoryKey)
        body = '{"characteristics": [{"value": false, "aid": 1, "iid": 8}]}' #json.dumps({'characteristics': [{'aid': 1, 'iid': 8, 'value': False}]}, indent=4)
        print(body)
        response = sec_http.put('/characteristics', body)
        data = response.read().decode()
        print(response.code, data)
        if response.code != 204:
            data = json.loads(data)
            code = data['status']
            print('identify failed because: {reason} ({code})'.format(reason=StatusCodes[code], code=code))

    elif args.operation == 'get_characteristics':
        if not args.characteristics:
            parser.print_help()
            sys.exit(-1)

        sec_http = SecureHttp(conn.sock, accessoryToControllerKey, controllerToAccessoryKey)
        response = sec_http.get('/characteristics?id=' + args.characteristics)
        print(response.status)
        data = json.loads(response.read().decode())
        print(json.dumps(data, indent=4))
    elif args.operation == 'get_accessories':
        sec_http = SecureHttp(conn.sock, accessoryToControllerKey, controllerToAccessoryKey)
        response = sec_http.get('/accessories')
        print(response.status)
        data = json.loads(response.read().decode())
        print(json.dumps(data, indent=4))
    else:
        print('not a valid operation')

    conn.close()
