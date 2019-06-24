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
import uuid
import ed25519
from binascii import hexlify

from homekit.controller import Controller
from homekit.controller.additional_pairing import AdditionalPairing
from homekit.log_support import setup_logging, add_log_arguments
from homekit.exceptions import AlreadyPairedError


def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit generate pairing data app')
    parser.add_argument('-f', action='store', required=True, dest='file', help='HomeKit pairing data file')
    parser.add_argument('-a', action='store', required=True, dest='alias', help='alias for the pairing')
    parser.add_argument('-i', action='store', required=True, dest='pairing_id', help='')
    parser.add_argument('-k', action='store', required=True, dest='key', help='')
    parser.add_argument('-p', action='store', required=True, dest='permission', choices=['User', 'Admin'], help='')
    add_log_arguments(parser)
    return parser.parse_args()

if __name__ == '__main__':
    args = setup_args_parser()

    setup_logging(args.loglevel)

    controller = Controller()
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
        data = pairing.add_pairing(args.pairing_id, args.key, args.permission)
    except Exception as e:
        print(e)
        logging.debug(e, exc_info=True)
        sys.exit(-1)
    

