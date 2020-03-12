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
import json
import tlv8
import base64

from homekit import AccessoryServer, Controller
from homekit.accessoryserver import AccessoryRequestHandler
from homekit.model import Accessory
from homekit.model.services import AbstractService, ServicesTypes
from homekit.model.characteristics import AbstractCharacteristic, CharacteristicFormats, CharacteristicsTypes
from homekit.http_impl import HttpStatusCodes


def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit debug mitm')
    parser.add_argument('--client-data', action='store', required=True, dest='client_data', default='./client.json')
    parser.add_argument('-a', action='store', required=True, dest='alias', help='alias for the pairing')
    parser.add_argument('--server-data', action='store', required=True, dest='server_data', default='./server.json')
    return parser.parse_args()


def setup_logging():
    global logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s %(filename)s:%(lineno)04d %(levelname)s %(message)s'))
    logger.addHandler(ch)


class ProxyService(AbstractService):
    def __init__(self, iid: int, service_type: str):
        AbstractService.__init__(self, service_type, iid)


class ProxyCharacteristic(AbstractCharacteristic):
    def __init__(self, iid: int, characteristic_type: str, characteristic_format: str):
        AbstractCharacteristic.__init__(self, iid, characteristic_type, characteristic_format)


def generate_set_value_callback(aid, characteristic: AbstractCharacteristic):
    def callback(value):
        iid = int(characteristic.iid)
        characteristics = [(int(aid), iid, value)]
        pairing.put_characteristics(characteristics)
        debug_value = value
        if characteristic.format == CharacteristicFormats.tlv8:
            bytes_value = base64.b64decode(value)
            debug_value = tlv8.format_string(tlv8.deep_decode(bytes_value))
        logger.info(
            'write value to {a}.{i} (type {t} / {u}): \n{v}'.format(a=aid, i=iid,
                                                                    u=characteristic.type,
                                                                    t=CharacteristicsTypes.get_short(
                                                                        characteristic.type),
                                                                    v=debug_value))

    return callback


def generate_get_value_callback(aid, characteristic: AbstractCharacteristic):
    def callback():
        iid = int(characteristic.iid)
        characteristics = [(int(aid), iid)]
        value = pairing.get_characteristics(characteristics)[(int(aid), int(iid))]['value']
        debug_value = value
        if characteristic.format == CharacteristicFormats.tlv8:
            bytes_value = base64.b64decode(value)
            debug_value = tlv8.format_string(tlv8.deep_decode(bytes_value))
        logger.info(
            'get value from {a}.{i} (type {t} / {u}): \n{v}'.format(a=aid, i=iid,
                                                                    u=characteristic.type,
                                                                    t=CharacteristicsTypes.get_short(
                                                                        characteristic.type),
                                                                    v=debug_value))

        return value

    return callback


def generate_proxy_accessory_request_handler(pairing):
    class ProxyAccessoryRequestHandler(AccessoryRequestHandler):

        def _post_resource(self):
            request_body = json.loads(self.body)
            try:
                (content_type, result_body) = pairing.get_resource(request_body)
                # logging.info('post resource with {v} results in {r}'.format(v=request_body, r=result_body))
                self.send_response(HttpStatusCodes.OK)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', len(result_body))
                self.end_headers()
                self.wfile.write(result_body)
            except Exception as e:
                logger.error('post resource with {v} results in exception {r}'.format(v=request_body, r=e))
                self.send_error(HttpStatusCodes.INTERNAL_SERVER_ERROR)

    return ProxyAccessoryRequestHandler


def create_proxy(accessories_and_characteristics):
    accessories = []
    logger.info('%<------ creating proxy ------')
    for accessory in accessories_and_characteristics:
        proxy_accessory = Accessory('', '', '', '', '', )
        aid = accessory['aid']
        proxy_accessory.aid = aid
        logger.info('accessory with aid=%s', aid)
        proxy_accessory.services = []
        accessories.append(proxy_accessory)

        for service in accessory['services']:
            service_iid = service['iid']
            service_type = service['type']
            short_type = ServicesTypes.get_short(service_type)
            logger.info('  %i.%i: >%s< (%s)', aid, service_iid, short_type, service_type)

            proxy_service = ProxyService(service_iid, service_type)
            proxy_accessory.add_service(proxy_service)

            for characteristic in service['characteristics']:
                characteristic_iid = characteristic['iid']
                characteristic_type = characteristic['type']
                short_type = CharacteristicsTypes.get_short(characteristic_type)
                characteristic_format = characteristic['format']
                characteristic_value = characteristic.get('value')
                characteristic_perms = characteristic['perms']
                logger.info('    %i.%i: %s >%s< (%s) [%s] %s', aid, characteristic_iid, characteristic_value,
                            short_type, characteristic_type, ','.join(characteristic_perms), characteristic_format)

                proxy_characteristic = ProxyCharacteristic(characteristic_iid, characteristic_type,
                                                           characteristic_format)
                proxy_service.append_characteristic(proxy_characteristic)
                if characteristic_value:
                    proxy_characteristic.value = characteristic_value
                proxy_characteristic.perms = characteristic_perms

                proxy_characteristic.set_set_value_callback(
                    generate_set_value_callback(accessory['aid'], proxy_characteristic))
                proxy_characteristic.set_get_value_callback(
                    generate_get_value_callback(accessory['aid'], proxy_characteristic))
    logger.info('%<------ finished creating proxy ------')
    return accessories


if __name__ == '__main__':
    args = setup_args_parser()

    setup_logging()

    client_config_file = os.path.expanduser(args.client_data)
    server_config_file = os.path.expanduser(args.server_data)

    controller = Controller()
    try:
        controller.load_data(client_config_file)
    except Exception as e:
        logger.error(e, exc_info=True)
        sys.exit(-1)

    if args.alias not in controller.get_pairings():
        logger.error('"%s" is no known alias', args.alias)
        sys.exit(-1)

    try:
        pairing = controller.get_pairings()[args.alias]
        data = pairing.list_accessories_and_characteristics()
    except Exception as e:
        logger.error(e, exc_info=True)
        sys.exit(-1)

    proxy_accessories = create_proxy(data)

    # create a server and an accessory an run it unless ctrl+c was hit
    try:
        httpd = AccessoryServer(server_config_file, logger,
                                request_handler_class=generate_proxy_accessory_request_handler(pairing))
        for proxy_accessory in proxy_accessories:
            httpd.add_accessory(proxy_accessory)

        httpd.publish_device()
        logger.info('published device and start serving')
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    # unpublish the device and shut down
    logger.info('unpublish device')
    httpd.unpublish_device()
    httpd.shutdown()
