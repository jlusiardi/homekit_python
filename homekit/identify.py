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

import sys
import argparse

from homekit.controller import Controller
from homekit.log_support import setup_logging, add_log_arguments


def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit identify app - performs identify on given HomeKit device')

    group = parser.add_argument_group('Identify unpaired', 'use this option to identify an UNPAIRED accessory.')
    group.add_argument('-d', action='store',  dest='device', help='accessory pairing id')

    group = parser.add_argument_group('Identify paired', 'use this option to identify an PAIRED accessory.')
    group.add_argument('-f', action='store',  dest='file', help='File with the pairing data')
    group.add_argument('-a', action='store', dest='alias', help='alias for the pairing')
    add_log_arguments(parser)

    parsed_args = parser.parse_args()

    if parsed_args.device and parsed_args.file is None and parsed_args.alias is None:
        # unpaired
        return parsed_args
    elif parsed_args.device is None and parsed_args.file and parsed_args.alias:
        # paired
        return parsed_args
    else:
        parser.print_help()
        sys.exit(-1)


if __name__ == '__main__':
    args = setup_args_parser()

    setup_logging(args.loglevel)

    controller = Controller()
    if args.device:
        controller.identify(args.device)
    else:
        controller.load_data(args.file)
        if args.alias not in controller.get_pairings():
            print('"{a}" is no known alias'.format(a=args.alias))
            exit(-1)

        pairing = controller.get_pairings()[args.alias]
        pairing.identify()
