#!/usr/bin/env python3

#
# Copyright 2018-2020 Joachim Lusiardi
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

import os.path
import logging
import argparse
import sys

from homekit import AccessoryServer, Controller
from homekit.model import Accessory
from homekit.model.services import AbstractService
from homekit.model.characteristics import AbstractCharacteristic


def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit debug mitm')
    parser.add_argument('--client-data', action='store', required=True, dest='client_data', default='./client.json')
    parser.add_argument('-a', action='store', required=True, dest='alias', help='alias for the pairing')
    parser.add_argument('--server-data', action='store', required=True, dest='server_data', default='./server.json')
    return parser.parse_args()


def setup_logging():
    global logger
    # setup logger
    logger = logging.getLogger('accessory')
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s %(filename)s:%(lineno)04d %(levelname)s %(message)s'))
    logger.addHandler(ch)
    logger.info('starting')


class MirrorService(AbstractService):
    def __init__(self, iid: int, service_type: str):
        AbstractService.__init__(self, service_type, iid)


class MirrorCharacteristic(AbstractCharacteristic):
    def __init__(self, iid: int, characteristic_type: str, characteristic_format: str):
        AbstractCharacteristic.__init__(self, iid, characteristic_type, characteristic_format)


if __name__ == '__main__':
    args = setup_args_parser()

    setup_logging()

    client_config_file = os.path.expanduser(args.client_data)
    server_config_file = os.path.expanduser(args.server_data)

    controller = Controller()
    try:
        controller.load_data(client_config_file)
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
    except Exception as e:
        print(e)
        logging.debug(e, exc_info=True)
        sys.exit(-1)

    accessories = []
    for accessory in data:
        mirror_accessory = Accessory('', '', '', '', '', )
        mirror_accessory.aid = accessory['aid']
        mirror_accessory.services = []
        accessories.append(mirror_accessory)

        for service in accessory['services']:
            service_iid = service['iid']
            service_type = service['type']
            mirror_service = MirrorService(service_iid, service_type)
            mirror_accessory.add_service(mirror_service)

            for characteristic in service['characteristics']:
                characteristic_iid = characteristic['iid']
                characteristic_type = characteristic['type']
                characteristic_format = characteristic['format']
                characteristic_value =  characteristic.get('value')
                characteristic_perms = characteristic['perms']
                mirror_characteristic = MirrorCharacteristic(characteristic_iid, characteristic_type, characteristic_format)
                mirror_service.append_characteristic(mirror_characteristic)
                if characteristic_value:
                    mirror_characteristic.value = characteristic_value
                mirror_characteristic.perms = characteristic_perms

                def generate_set_value_callback(aid, iid):
                    def callback(value):
                        characteristics = [(int(aid), int(iid), value)]
                        pairing.put_characteristics(characteristics)
                        print('set callback', characteristics)
                    return callback

                def generate_get_value_callback(aid, iid):
                    def callback():
                        characteristics = [(int(aid), int(iid))]
                        value = pairing.get_characteristics(characteristics)
                        print('get callback', characteristics, value)
                        return value[(int(aid), int(iid))]
                    return callback

                mirror_characteristic.set_set_value_callback(generate_set_value_callback(accessory['aid'], characteristic_iid))
                mirror_characteristic.set_get_value_callback(generate_get_value_callback(accessory['aid'], characteristic_iid))

    # create a server and an accessory an run it unless ctrl+c was hit
    try:
        httpd = AccessoryServer(server_config_file, logger)
        for accessory in accessories:
            httpd.add_accessory(accessory)

        httpd.publish_device()
        logger.info('published device and start serving')
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    # unpublish the device and shut down
    logger.info('unpublish device')
    httpd.unpublish_device()
    httpd.shutdown()
