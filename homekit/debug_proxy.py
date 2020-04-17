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
import functools

from homekit import AccessoryServer, Controller
from homekit.accessoryserver import AccessoryRequestHandler
from homekit.model import Accessory
from homekit.model.services import AbstractService, ServicesTypes
from homekit.model.characteristics import AbstractCharacteristic, CharacteristicFormats, CharacteristicsTypes, \
    CharacteristicsDecoderLoader
from homekit.http_impl import HttpStatusCodes
from homekit.controller.tools import AbstractPairing
from homekit.log_support import setup_logging, add_log_arguments

# global containers for the filter functions
get_filters = {}
set_filters = {}


def log_loaded_filter_count():
    """
    logs the numbers of loaded filters.
    """

    def count_filters(filters):
        count = 0
        for accessory_data in filters.items():
            count += len(accessory_data[1].items())
        return count

    logging.info('loaded %i set_filter functions', count_filters(set_filters))
    logging.info('loaded %i get_filter functions', count_filters(get_filters))


def get_filter(aid, cid):
    """
    The get_filter decorator. This adds the decorated function to the global list of get_filters for later usage. The
    original function is also surrounded to return a value in any case. If the decorated function returns None, the
    original value is returned instead.

    :param aid: the accessory's id
    :param cid: the characteristic's id
    :return: a function decorating the filter function
    """

    def decorator_getter(func):
        @functools.wraps(func)
        def decorated(val):
            new_val = func(val)
            if new_val is None:
                return val
            else:
                return new_val

        if aid not in get_filters:
            get_filters[aid] = {}
        if cid in get_filters[aid]:
            raise Exception()
        else:
            get_filters[aid][cid] = func

        return decorated

    return decorator_getter


def set_filter(aid, cid):
    """
    The set_filter decorator. This adds the decorated function to the global list of set_filters for later usage. The
    original function is also surrounded to return a value in any case. If the decorated function returns None, the
    original value is returned instead.

    :param aid: the accessory's id
    :param cid: the characteristic's id
    :return: a function decorating the filter function
    """

    def decorator_setter(func):
        @functools.wraps(func)
        def decorated(val):
            new_val = func(val)
            if new_val is None:
                return val
            else:
                return new_val

        if aid not in set_filters:
            set_filters[aid] = {}
        if cid in set_filters[aid]:
            raise Exception()
        else:
            set_filters[aid][cid] = decorated

        return decorated

    return decorator_setter


def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit debug proxy')
    parser.add_argument('-c', '--client-data', action='store', required=True, dest='client_data',
                        default='./client.json', help='JSON file with the pairing data for the accessory')
    parser.add_argument('-a', '--alias', action='store', required=True, dest='alias', help='alias for the pairing')
    parser.add_argument('-s', '--server-data', action='store', required=True, dest='server_data',
                        default='./server.json', help='JSON file with the accessory data to the controller')
    parser.add_argument('-C', '--code', action='store', required=False, dest='code',
                        help='Reference to a python module with filter functions')
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


decoder_loader = CharacteristicsDecoderLoader()


def log_transferred_value(text: str, aid: int, characteristic: AbstractCharacteristic, value, filtered_value):
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
    filtered_debug_value = filtered_value
    characteristic_name = CharacteristicsTypes.get_short(characteristic.type)
    if characteristic.format == CharacteristicFormats.tlv8:
        bytes_value = base64.b64decode(value)
        filtered_bytes_value = base64.b64decode(filtered_value)
        decoder = decoder_loader.load(characteristic.type)
        if decoder:
            try:
                debug_value = tlv8.format_string(decoder(bytes_value))
                filtered_debug_value = tlv8.format_string(decoder(filtered_bytes_value))
            except Exception as e:
                logging.error('problem decoding', e)
        else:
            debug_value = tlv8.format_string(tlv8.deep_decode(bytes_value))
            filtered_debug_value = tlv8.format_string(tlv8.deep_decode(filtered_bytes_value))
    logging.info(
        '%s %s.%s (type %s / %s): \n\toriginal value: %s\n\tfiltered value: %s' % (
            text, aid, iid, characteristic.type, characteristic_name, debug_value, filtered_debug_value))


def generate_set_value_callback(aid: int, characteristic: AbstractCharacteristic, set_filters):
    """
    generate a call back function for the set value use case. This also logs the transferred value.

    :param aid: the id of the accessory
    :param characteristic: the characteristic that is read
    :return: the value as if it would come directly from the proxied device.
    """

    def callback(value):
        iid = int(characteristic.iid)

        # put value through possible filter
        filtered_value = set_filters.get(aid, {}).get(iid, lambda x: x)(value)

        # now log the value
        log_transferred_value('write value to', aid, characteristic, value, filtered_value)

        # set the value on the proxied device
        characteristics = [(aid, iid, filtered_value)]
        pairing.put_characteristics(characteristics)

    return callback


def generate_get_value_callback(aid: int, characteristic: AbstractCharacteristic, get_filters):
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

        # put value through possible filter
        filtered_value = get_filters.get(aid, {}).get(iid, lambda x: x)(value)

        # now log the value
        log_transferred_value('get value from', aid, characteristic, value, filtered_value)

        # return the value from the proxied device
        return filtered_value

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
                    generate_set_value_callback(accessory['aid'], proxy_characteristic, set_filters))
                proxy_characteristic.set_get_value_callback(
                    generate_get_value_callback(accessory['aid'], proxy_characteristic, get_filters))
    logging.info('%<------ finished creating proxy ------')
    return accessories


if __name__ == '__main__':
    args = setup_args_parser()

    setup_logging(args.loglevel)

    client_config_file = os.path.expanduser(args.client_data)
    server_config_file = os.path.expanduser(args.server_data)

    if args.code:
        logging.info('loading filters from "%s"', args.code)
        try:
            module = importlib.import_module(args.code)
            set_filters = getattr(module, 'set_filters')
            get_filters = getattr(module, 'get_filters')
        except Exception as e:
            url = 'https://github.com/jlusiardi/homekit_python/tree/master#filter-functions'
            logging.error('error loading from "%s": %s (see %s for more information)', args.code, e, url)
            sys.exit(-1)
        log_loaded_filter_count()

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
