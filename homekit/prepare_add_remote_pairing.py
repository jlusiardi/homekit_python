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

    try:
        pairings = controller.get_pairings()
        if args.alias in pairings:
            pairing_data = pairings[args.alias]._get_pairing_data()
            additional_controller_pairing_identifier = pairing_data['iOSPairingId']
            ios_device_ltpk = pairing_data['iOSDeviceLTPK']
            text = 'Alias "{a}" is already in state add additional pairing.\n'\
                   'Please add this to homekit.add_additional_pairing:\n'\
                   '    -i {id} -k {pk}'\
                   .format(a=args.alias,
                           id=additional_controller_pairing_identifier,
                           pk=ios_device_ltpk
                           )
            raise AlreadyPairedError(text)

        additional_controller_pairing_identifier = str(uuid.uuid4())
        ios_device_ltsk, ios_device_ltpk = ed25519.create_keypair()

        public_key = hexlify(ios_device_ltpk.to_bytes()).decode()

        text = 'Please add this to homekit.add_additional_pairing:\n' \
               '    -i {id} -k {pk}' \
            .format(a=args.alias,
                    id=additional_controller_pairing_identifier,
                    pk=public_key
                    )
        print(text)

        a = {
            'iOSPairingId': additional_controller_pairing_identifier,
            'iOSDeviceLTSK': ios_device_ltsk.to_ascii(encoding='hex').decode()[:64],
            'iOSDeviceLTPK': public_key,
            'Connection': 'ADDITIONAL_PAIRING'
        }
        pairings[args.alias] = AdditionalPairing(a)
        controller.save_data(args.file)
    except Exception as e:
        print(e)
        logging.debug(e, exc_info=True)
        sys.exit(-1)
