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

from homekit.log_support import setup_logging, add_log_arguments
from homekit.controller import Controller


def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit IP discover app -'
                                                 ' list all HomeKit devices on the same IP network')
    parser.add_argument('-t', action='store', required=False, dest='timeout', type=int, default=10,
                        help='Number of seconds to wait')
    add_log_arguments(parser)
    return parser.parse_args()


if __name__ == '__main__':
    args = setup_args_parser()
    setup_logging(args.loglevel)

    results = Controller.discover(args.timeout)
    for info in results:
        # TODO wait for result of https://github.com/jlusiardi/homekit_python/issues/40
        print('Name: {name}'.format(name=info['name']))
        print('Url: http_impl://{ip}:{port}'.format(ip=info['address'], port=info['port']))
        print('Configuration number (c#): {conf}'.format(conf=info['c#']))
        print('Feature Flags (ff): {f} (Flag: {flags})'.format(f=info['flags'], flags=info['ff']))
        print('Device ID (id): {id}'.format(id=info['id']))
        print('Model Name (md): {md}'.format(md=info['md']))
        print('Protocol Version (pv): {pv}'.format(pv=info['pv']))
        print('State Number (s#): {sn}'.format(sn=info['s#']))
        print('Status Flags (sf): {sf}'.format(sf=info['sf']))
        print('Category Identifier (ci): {c} (Id: {ci})'.format(c=info['category'], ci=info['ci']))
        print()
