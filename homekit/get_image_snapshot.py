# !/usr/bin/env python3

#
# Copyright 2020 Joachim Lusiardi
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
    parser = argparse.ArgumentParser(description='HomeKit get_resource - retrieve value of snapshot '
                                                 'resource  from paired HomeKit accessories.')
    parser.add_argument('-f', action='store', required=True, dest='file', help='File with the pairing data')
    parser.add_argument('-a', action='store', required=True, dest='alias', help='alias for the pairing')
    parser.add_argument('-A', action='store', dest='accessory_id', help='Accessory id for the camera (optional)')
    parser.add_argument('-o', action='store', required=True, dest='output',
                        help='Name of the file for the loaded image')
    parser.add_argument('-W', action='store', default=640, type=int, dest='width', help='Width of the loaded image')
    parser.add_argument('-H', action='store', default=480, type=int, dest='height', help='Height of the loaded image')
    add_log_arguments(parser)
    return parser.parse_args()


if __name__ == '__main__':
    args = setup_args_parser()

    setup_logging(args.loglevel)

    controller = Controller()
    controller.load_data(args.file)
    if args.alias not in controller.get_pairings():
        print('"{a}" is no known alias'.format(a=args.alias))
        sys.exit(-1)

    pairing = controller.get_pairings()[args.alias]

    # get the data
    try:
        resource_request = {
            'resource-type': 'image',
            'image-width': args.width,
            'image-height': args.height
        }
        if args.accessory_id:
            resource_request['aid'] = args.accessory_id
        data = pairing.get_resource(resource_request)
    except Exception as e:
        print(e)
        logging.debug(e, exc_info=True)
        sys.exit(-1)

    # write the data to a file
    with open(args.output, 'wb') as output_file:
        output_file.write(data.content)
