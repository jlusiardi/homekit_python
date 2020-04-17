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
import sys
import logging
import tlv8
import base64

from homekit.controller import Controller
from homekit.log_support import setup_logging, add_log_arguments
from homekit.model.characteristics import CharacteristicsDecoderLoader
from homekit.controller.tools import AbstractPairing
from homekit.model.characteristics.characteristic_formats import CharacteristicFormats


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
    parser.add_argument('-d', action='store_true', required=False, dest='decode',
                        help='If set, try to find a decoder for each characteristic and show the decoded value')
    parser.add_argument('--adapter', action='store', dest='adapter', default='hci0',
                        help='the bluetooth adapter to be used (defaults to hci0)')
    add_log_arguments(parser)
    return parser.parse_args()


def get_characteristic_decoders(pairing: AbstractPairing) -> dict:
    """
    This function filters characteristics of an accessory for decodable types (currently only TLV characteristics) and
    tries to load the decoder functions for said characteristic's uuid.

    :param pairing: an implementation of `AbstractPairing` (either for IP or BLE)
    :return: a dict of aid/cid to decoder functions
    """
    loaded_decoders = {}
    loader = CharacteristicsDecoderLoader()
    for a in pairing.list_accessories_and_characteristics():
        aid = a['aid']
        for s in a['services']:
            for c in s['characteristics']:
                c_format = c['format']
                # TODO what about CharacteristicFormats.data?
                if c_format not in [CharacteristicFormats.tlv8]:
                    continue
                c_id = c['iid']
                key = '{}.{}'.format(aid, c_id)
                c_type = c['type']
                decoder = loader.load(c_type)
                if decoder is not None:
                    loaded_decoders[key] = decoder

    return loaded_decoders


if __name__ == '__main__':
    args = setup_args_parser()

    setup_logging(args.loglevel)

    controller = Controller(args.adapter)
    controller.load_data(args.file)
    if args.alias not in controller.get_pairings():
        print('"{a}" is no known alias'.format(a=args.alias))
        sys.exit(-1)

    pairing = controller.get_pairings()[args.alias]

    # convert the command line parameters to the required form
    characteristics = [(int(c.split('.')[0]), int(c.split('.')[1])) for c in args.characteristics]

    # get the data
    try:
        data = pairing.get_characteristics(characteristics, include_meta=args.meta, include_perms=args.perms,
                                           include_type=args.type, include_events=args.events)
    except Exception as e:
        print(e)
        logging.debug(e, exc_info=True)
        sys.exit(-1)

    if args.decode:
        decoders = get_characteristic_decoders(pairing)
    else:
        decoders = {}

    # print the data
    tmp = {}
    for k in data:
        nk = str(k[0]) + '.' + str(k[1])
        value = data[k]

        if decoders.get(nk):
            try:
                value['value'] = decoders.get(nk)(base64.b64decode(value['value']))
            except Exception as e:
                logging.ERROR('could not decode', e)

        tmp[nk] = value

    print(json.dumps(tmp, indent=4, cls=tlv8.JsonEncoder))
