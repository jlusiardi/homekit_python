#!/usr/bin/env python3

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

import os.path
import logging
import argparse
import sys
import json
import tlv8
import base64
import importlib

from homekit import AccessoryServer, Controller
from homekit.accessoryserver import AccessoryRequestHandler
from homekit.model import Accessory
from homekit.model.services import AbstractService, ServicesTypes
from homekit.model.characteristics import AbstractCharacteristic, CharacteristicFormats, CharacteristicsTypes
from homekit.http_impl import HttpStatusCodes
from homekit.controller.tools import AbstractPairing
from homekit.log_support import setup_logging, add_log_arguments


def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit debug mitm')
    parser.add_argument('-c', '--client-data', action='store', required=True, dest='client_data',
                        default='./client.json')
    parser.add_argument('-a', '--alias', action='store', required=True, dest='alias', help='alias for the pairing')
    parser.add_argument('-s', '--server-data', action='store', required=True, dest='server_data',
                        default='./server.json')
    add_log_arguments(parser, 'INFO')
    return parser.parse_args()


class ProxyService(AbstractService):
    """
    Implementation of `AbstractService` to act as a proxy.
    """

    def __init__(self, iid: int, service_type: str):
        AbstractService.__init__(self, service_type, iid)


class ProxyCharacteristic(AbstractCharacteristic):
    """
    Implementation of `AbstractCharacteristic` to act as a proxy.
    """

    def __init__(self, iid: int, characteristic_type: str, characteristic_format: str):
        AbstractCharacteristic.__init__(self, iid, characteristic_type, characteristic_format)


class CharacteristicsDecoderLoader:
    """
    class to dynamically load decoders for tlv8 characteristics.
    """

    def __init__(self):
        self.decoders = {}

    def load(self, char_type: str):
        """
        This function loads a decoder for the specified characteristics:
         - get the name of the characteristic via the given uuid (via `CharacteristicsTypes.get_short()`)
         - load a module from `homekit.model.characteristics` plus the name of the characteristic
         - the module must contain a function `decoder`

        :param char_type: the uuid of the characteristic
        :return: a function that decodes the value of the characteristic into a `tlv8.EntryList`
        """
        characteristic_name = CharacteristicsTypes.get_short(char_type)
        mod_name = characteristic_name.replace('-', '_')
        if char_type not in self.decoders:
            try:
                logging.info('loading module %s for type %s', mod_name, char_type)
                module = importlib.import_module('homekit.model.characteristics.' + mod_name)
                decoder = getattr(module, 'decoder')
                self.decoders[char_type] = decoder
                return decoder
            except Exception as e:
                logging.error('Error loading decoder: %s for type %s', e, char_type)
                return None
        else:
            logging.info('got decoder for %s from cache', char_type)
            return self.decoders[char_type]


decoder_loader = CharacteristicsDecoderLoader()


def log_transferred_value(text: str, aid: int, characteristic: AbstractCharacteristic, value):
    """
    Logs the transfer of a value between controller and acccessory or vice versa. For characteristics
    of type TLV8, a decoder is used if available else a deep decode is done.

    :param text: a `str` to express which direction of transfer takes place
    :param aid: the accessory id
    :param characteristic: the characteristic for which the transfer takes place
    :param value: the value that was transferred
    """
    iid = int(characteristic.iid)
    debug_value = value
    characteristic_name = CharacteristicsTypes.get_short(characteristic.type)
    if characteristic.format == CharacteristicFormats.tlv8:
        bytes_value = base64.b64decode(value)
        decoder = decoder_loader.load(characteristic.type)
        if decoder:
            debug_value = tlv8.format_string(decoder(bytes_value))
        else:
            debug_value = tlv8.format_string(tlv8.deep_decode(bytes_value))
    logging.info(
        '%s %s.%s (type %s / %s): \n%s' % (
            text, aid, iid, characteristic.type, characteristic_name, debug_value))


def generate_set_value_callback(aid: int, characteristic: AbstractCharacteristic):
    """
    generate a call back function for the set value use case. This also logs the transferred value.

    :param aid: the id of the accessory
    :param characteristic: the characteristic that is read
    :return: the value as if it would come directly from the proxied device.
    """

    def callback(value):
        iid = int(characteristic.iid)

        # set the value on the proxied device
        characteristics = [(aid, iid, value)]
        pairing.put_characteristics(characteristics)

        # now log the value
        log_transferred_value('write value to', aid, characteristic, value)

    return callback


def generate_get_value_callback(aid: int, characteristic: AbstractCharacteristic):
    """
    generate a call back function for the get value use case. This also logs the transferred value.

    :param aid: the id of the accessory
    :param characteristic: the characteristic that is read
    :return: the value as if it would come directly from the proxied device.
    """

    def callback():
        iid = int(characteristic.iid)
        characteristics = [(aid, iid)]
        value = pairing.get_characteristics(characteristics)[(int(aid), int(iid))]['value']

        # now log the value
        log_transferred_value('get value from', aid, characteristic, value)

        # return the value from the proxied device
        return value

    return callback


def generate_proxy_accessory_request_handler(pairing: AbstractPairing):
    """
    Generate a subclass of `AccessoryRequestHandler` whose method `_post_resource` was over written to proxy all calls
    to the accessory represented by the given pairing. Logs are also done.

    :param pairing: an instance of `AbstractPairing`
    :return: a subclass that can be used as `request_handler_class` for an `AccessoryServer`
    """

    class ProxyAccessoryRequestHandler(AccessoryRequestHandler):

        def _post_resource(self):
            request_body = json.loads(self.body)
            try:
                (content_type, result_body) = pairing.get_resource(request_body)
                logging.info(
                    'post resource with {v} results in {t} with {r} bytes'.format(v=request_body, t=content_type,
                                                                                  r=len(result_body)))
                self.send_response(HttpStatusCodes.OK)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', len(result_body))
                self.end_headers()
                self.wfile.write(result_body)
            except Exception as e:
                logging.error('post resource with {v} results in exception {r}'.format(v=request_body, r=e))
                self.send_error(HttpStatusCodes.INTERNAL_SERVER_ERROR)

    return ProxyAccessoryRequestHandler


def create_proxy(accessories_and_characteristics):
    """
    Create a proxy in front of a set of accessories, services and characteristics. This allows to follow the
    communication of a controller and an accessory (e.g. an iPhone and some HomeKit IP camera).

    :param accessories_and_characteristics: the accessory data as described in the spec on page 73 and following. This
    contains all the data that will be used to create the proxy.
    :return: a list of `Accessory` instances whose services and characteristics are replaced by proxied versions. That
    means characteristic's callback functions for getting and setting values relay those calls to the proxied
    characteristics.
    """
    accessories = []
    logging.info('%<------ creating proxy ------')
    for accessory in accessories_and_characteristics:
        proxy_accessory = Accessory('', '', '', '', '', )
        aid = accessory['aid']
        proxy_accessory.aid = aid
        logging.info('accessory with aid=%s', aid)
        proxy_accessory.services = []
        accessories.append(proxy_accessory)

        for service in accessory['services']:
            service_iid = service['iid']
            service_type = service['type']
            short_type = ServicesTypes.get_short(service_type)
            logging.info('  %i.%i: >%s< (%s)', aid, service_iid, short_type, service_type)

            proxy_service = ProxyService(service_iid, service_type)
            proxy_accessory.add_service(proxy_service)

            for characteristic in service['characteristics']:
                characteristic_iid = characteristic['iid']
                characteristic_type = characteristic['type']
                short_type = CharacteristicsTypes.get_short(characteristic_type)
                characteristic_format = characteristic['format']
                characteristic_value = characteristic.get('value')
                characteristic_perms = characteristic['perms']
                logging.info('    %i.%i: %s >%s< (%s) [%s] %s', aid, characteristic_iid, characteristic_value,
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
    logging.info('%<------ finished creating proxy ------')
    return accessories


if __name__ == '__main__':
    args = setup_args_parser()

    setup_logging(args.loglevel)

    client_config_file = os.path.expanduser(args.client_data)
    server_config_file = os.path.expanduser(args.server_data)

    controller = Controller()
    try:
        controller.load_data(client_config_file)
    except Exception as e:
        logging.error(e, exc_info=True)
        sys.exit(-1)

    if args.alias not in controller.get_pairings():
        logging.error('"%s" is no known alias', args.alias)
        sys.exit(-1)

    try:
        pairing = controller.get_pairings()[args.alias]
        data = pairing.list_accessories_and_characteristics()
    except Exception as e:
        logging.error(e, exc_info=True)
        sys.exit(-1)

    proxy_accessories = create_proxy(data)

    # create a server and an accessory an run it unless ctrl+c was hit
    try:
        httpd = AccessoryServer(server_config_file, logging.getLogger(),
                                request_handler_class=generate_proxy_accessory_request_handler(pairing))
        for proxy_accessory in proxy_accessories:
            httpd.add_accessory(proxy_accessory)

        httpd.publish_device()
        logging.info('published device and start serving')
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    # unpublish the device and shut down
    logging.info('unpublish device')
    httpd.unpublish_device()
    httpd.shutdown()
