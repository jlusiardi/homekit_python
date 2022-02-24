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

import argparse

from homekit.controller import Controller
from homekit.log_support import setup_logging, add_log_arguments


def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit remove pairing app')
    parser.add_argument('-f', action='store', required=True, dest='file', help='File with the pairing data')
    parser.add_argument('-a', action='store', required=True, dest='alias',
                        help='alias for the accessory')
    parser.add_argument('-i', action='store', required=False, dest='controllerPairingId',
                        help='this pairing ID identifies the controller who should be removed from accessory')
    parser.add_argument('--adapter', action='store', dest='adapter', default='hci0',
                        help='the bluetooth adapter to be used (defaults to hci0)')
    parser.add_argument('--force', action='store_true', dest='force',
                        help='force removing of pairing in pairing data even if accessory is not reachable')
    add_log_arguments(parser)
    return parser.parse_args()


if __name__ == '__main__':
    args = setup_args_parser()

    setup_logging(args.loglevel)

    controller = Controller(args.adapter)
    controller.load_data(args.file)
    if args.alias not in controller.get_pairings():
        print('"{a}" is no known alias'.format(a=args.alias))
        exit(-1)

    controller.remove_pairing(args.alias, args.controllerPairingId, args.force)
    controller.save_data(args.file)
    print('Pairing for "{a}" was removed.'.format(a=args.alias))
