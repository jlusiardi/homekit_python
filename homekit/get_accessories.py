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
import sys
import argparse
import logging
import tlv8
import base64

from homekit.controller import Controller
from homekit.model.characteristics import CharacteristicsTypes, CharacteristicsDecoderLoader
from homekit.model.services import ServicesTypes
from homekit.log_support import setup_logging, add_log_arguments
from homekit.model.characteristics.characteristic_formats import CharacteristicFormats


def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit get accessories app')
    parser.add_argument('-f', action='store', required=True, dest='file', help='File with the pairing data')
    parser.add_argument('-a', action='store', required=True, dest='alias', help='alias for the pairing')
    parser.add_argument('-o', action='store', dest='output', default='compact', choices=['json', 'compact'],
                        help='Specify output format')
    parser.add_argument('--adapter', action='store', dest='adapter', default='hci0',
                        help='the bluetooth adapter to be used (defaults to hci0)')
    parser.add_argument('-d', action='store_true', required=False, dest='decode',
                        help='If set, try to find a decoder for each characteristic and show the decoded value')
    add_log_arguments(parser)
    return parser.parse_args()


def decode_values(input_data):
    """
    Try to decode the values from the given data structure. This depends on:
     - if the field is of type `CharacteristicFormats.tlv8`
     - a decoder was found for the characteristic

    :param input_data: data returned from `AbstractPairing.list_accessories_and_characteristics`
    :return: the input data with decoded value fields
    """
    loader = CharacteristicsDecoderLoader()
    for accessory in input_data:
        for service in accessory['services']:
            for characteristic in service['characteristics']:
                c_format = characteristic['format']
                c_type = characteristic['type']
                # TODO what about CharacteristicFormats.data?
                if c_format in [CharacteristicFormats.tlv8]:
                    decoder = loader.load(c_type)
                    if decoder:
                        try:
                            characteristic['value'] = decoder(base64.b64decode(characteristic['value']))
                        except Exception as e:
                            logging.error('error during decode %s: %s' % (c_type, characteristic['value']), e)
    return input_data


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
        data = pairing.list_accessories_and_characteristics()
        controller.save_data(args.file)
    except Exception as e:
        print(e)
        logging.debug(e, exc_info=True)
        sys.exit(-1)

    if args.decode:
        data = decode_values(data)

    # prepare output
    if args.output == 'json':
        print(json.dumps(data, indent=4, cls=tlv8.JsonEncoder))

    if args.output == 'compact':
        for accessory in data:
            aid = accessory['aid']
            for service in accessory['services']:
                s_type = service['type']
                s_iid = service['iid']
                print('{aid}.{iid}: >{stype}<'.format(aid=aid, iid=s_iid, stype=ServicesTypes.get_short(s_type)))

                for characteristic in service['characteristics']:
                    c_iid = characteristic['iid']
                    value = characteristic.get('value', '')
                    c_type = characteristic['type']
                    c_format = characteristic['format']
                    # we need to get the entry list from the decoder into a string and reformat it for better
                    # readability.
                    if args.decode and c_format in [CharacteristicFormats.tlv8] and isinstance(value, tlv8.EntryList):
                        value = tlv8.format_string(value)
                        value = '      '.join(value.splitlines(keepends=True))
                        value = '\n      ' + value
                    perms = ','.join(characteristic['perms'])
                    desc = characteristic.get('description', '')
                    c_type = CharacteristicsTypes.get_short(c_type)
                    print('  {aid}.{iid}: ({description}) >{ctype}< [{perms}]'.format(aid=aid,
                                                                                      iid=c_iid,
                                                                                      ctype=c_type,
                                                                                      perms=perms,
                                                                                      description=desc))
                    print('    Value: {value}'.format(value=value))
