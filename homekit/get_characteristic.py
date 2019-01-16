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

from homekit.controller import Controller
from homekit.log_support import setup_logging, add_log_arguments


def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit get_characteristic - retrieve values of characteristics '
                                                 'and other information from paired HomeKit accessories.')
    parser.add_argument('-f', action='store', required=True, dest='file', help='File with the pairing data')
    parser.add_argument('-a', action='store', required=True, dest='alias', help='alias for the pairing')
    parser.add_argument('-c', action='append', required=True, dest='characteristics',
                        help='Read characteristics, multiple characteristics can be given by repeating the option')
    parser.add_argument('-m', action='store_true', required=False, dest='meta',
                        help='read out the meta data for the characteristics as well')
    parser.add_argument('-p', action='store_true', required=False, dest='perms',
                        help='read out the permissions for the characteristics as well')
    parser.add_argument('-t', action='store_true', required=False, dest='type',
                        help='read out the types for the characteristics as well')
    parser.add_argument('-e', action='store_true', required=False, dest='events',
                        help='read out the events for the characteristics as well')
    add_log_arguments(parser)
    return parser.parse_args()


if __name__ == '__main__':
    args = setup_args_parser()

    setup_logging(args.loglevel)

    controller = Controller()
    controller.load_data(args.file)
    if args.alias not in controller.get_pairings():
        print('"{a}" is no known alias'.format(a=args.alias))
        exit(-1)

    pairing = controller.get_pairings()[args.alias]

    # convert the command line parameters to the required form
    characteristics = [(int(c.split('.')[0]), int(c.split('.')[1])) for c in args.characteristics]

    # get the data
    data = pairing.get_characteristics(characteristics, include_meta=args.meta, include_perms=args.perms,
                                       include_type=args.type, include_events=args.events)

    # print the data
    tmp = {}
    for k in data:
        nk = str(k[0]) + '.' + str(k[1])
        tmp[nk] = data[k]

    print(json.dumps(tmp, indent=4))
