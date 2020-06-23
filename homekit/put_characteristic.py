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
import sys
import logging

from homekit.controller import Controller
from homekit.log_support import setup_logging, add_log_arguments


def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit put_characteristic app - change values of characteristics '
                                                 'on paired HomeKit accessories.')
    parser.add_argument('-f', action='store', required=True, dest='file', help='File with the pairing data')
    parser.add_argument('-a', action='store', required=True, dest='alias', help='alias for the pairing')
    parser.add_argument('-c', action='append', required=False, dest='characteristics', nargs=2,
                        help='Use `aid.iid value` to change the value. Repeat to change multiple characteristics. '
                             'If the value starts with `@` it is interpreted as a file')
    parser.add_argument('--adapter', action='store', dest='adapter', default='hci0',
                        help='the bluetooth adapter to be used (defaults to hci0)')
    add_log_arguments(parser)

    args = parser.parse_args()
    if 'characteristics' not in args or not args.characteristics:
        parser.print_help()
        sys.exit(-1)
    return args


def handle_file_values(characteristics):
    tmp = []
    for characteristic in characteristics:
        val = characteristic[2]
        if isinstance(val, str) and val.startswith('@'):
            filename = val[1:]
            with open(filename, 'r') as input_file:
                val = input_file.read()
        tmp.append((characteristic[0], characteristic[1], val, ))
    return tmp


if __name__ == '__main__':
    args = setup_args_parser()

    setup_logging(args.loglevel)

    controller = Controller(args.adapter)
    try:
        controller.load_data(args.file)
    except Exception as e:
        print(e)
        logging.debug(e, exc_info=True)
        sys.exit(-1)

    if args.alias not in controller.get_pairings():
        print('"{a}" is no known alias'.format(a=args.alias))
        sys.exit(-1)

    try:
        pairing = controller.get_pairings()[args.alias]

        characteristics = [(int(c[0].split('.')[0]),  # the first part is the aid, must be int
                            int(c[0].split('.')[1]),  # the second part is the iid, must be int
                            c[1]) for c in args.characteristics]
        characteristics = handle_file_values(characteristics)
        results = pairing.put_characteristics(characteristics, do_conversion=True)
    except Exception as e:
        print(e)
        logging.debug(e, exc_info=True)
        sys.exit(-1)

    for key, value in results.items():
        aid = key[0]
        iid = key[1]
        status = value['status']
        desc = value['description']
        # used to be < 0 but bluetooth le errors are > 0 and only success (= 0) needs to be checked
        if status != 0:
            print('put_characteristics failed on {aid}.{iid} because: {reason} ({code})'.format(aid=aid, iid=iid,
                                                                                                reason=desc,
                                                                                                code=status))
