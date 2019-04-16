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

import os.path
import logging
import argparse

from homekit import AccessoryServer
from homekit.model import Accessory
from homekit.model.services import LightBulbService


def light_switched(new_value):
    print('=======>  light switched: {x}'.format(x=new_value))


def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit demo server')
    parser.add_argument('-f', action='store', required=False, dest='file', default='./demoserver.json',
                        help='File with the config data (defaults to ./demoserver.json)')
    return parser.parse_args()


if __name__ == '__main__':
    args = setup_args_parser()

    # setup logger
    logger = logging.getLogger('accessory')
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(ch)
    logger.info('starting')

    config_file = os.path.expanduser(args.file)

    # create a server and an accessory an run it unless ctrl+c was hit
    try:
        httpd = AccessoryServer(config_file, logger)

        accessory = Accessory('Testlicht', 'lusiardi.de', 'Demoserver', '0001', '0.1')
        lightBulbService = LightBulbService()
        lightBulbService.set_on_set_callback(light_switched)
        accessory.services.append(lightBulbService)
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

