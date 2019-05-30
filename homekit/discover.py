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
import locale

from homekit.log_support import setup_logging, add_log_arguments
from homekit.controller import Controller


def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit IP discover app -'
                                                 ' list all HomeKit devices on the same IP network')
    parser.add_argument('-t', action='store', required=False, dest='timeout', type=int, default=10,
                        help='Number of seconds to wait')
    parser.add_argument('-u', action='store_true', required=False, dest='unpaired_only',
                        help='If activated, this option will show only unpaired HomeKit IP Devices')
    add_log_arguments(parser)
    return parser.parse_args()


def prepare_string(input_string):
    """
    Make a string save for printing in a terminal. The string get recoded using the terminals preferred locale and
    replacing the characters that cannot be encoded.
    :param input_string: the input string
    :return: the output string which is save for printing
    """
    return '{t}'.format(t=input_string.encode(locale.getpreferredencoding(), errors='replace').decode())


if __name__ == '__main__':
    args = setup_args_parser()
    setup_logging(args.loglevel)

    results = Controller.discover(args.timeout)
    for info in results:
        if args.unpaired_only and info['sf'] == '0':
            continue
        print('Name: {name}'.format(name=prepare_string(info['name'])))
        print('Url: http_impl://{ip}:{port}'.format(ip=info['address'], port=info['port']))
        print('Configuration number (c#): {conf}'.format(conf=info['c#']))
        print('Feature Flags (ff): {f} (Flag: {flags})'.format(f=info['flags'], flags=info['ff']))
        print('Device ID (id): {id}'.format(id=info['id']))
        print('Model Name (md): {md}'.format(md=prepare_string(info['md'])))
        print('Protocol Version (pv): {pv}'.format(pv=info['pv']))
        print('State Number (s#): {sn}'.format(sn=info['s#']))
        print('Status Flags (sf): {sf} (Flag: {flags})'.format(sf=info['statusflags'], flags=info['sf']))
        print('Category Identifier (ci): {c} (Id: {ci})'.format(c=info['category'], ci=info['ci']))
        print()
