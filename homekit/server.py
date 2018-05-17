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

from http.server import HTTPServer
from socketserver import ThreadingMixIn
from zeroconf import Zeroconf, ServiceInfo
import socket
import sys
import logging

from homekit.serverdata import HomeKitServerData
from homekit.request_handler import HomeKitRequestHandler
from homekit.model import Accessories, Categories


class HomeKitServer(ThreadingMixIn, HTTPServer):
    def __init__(self, config_file, logger=sys.stderr):
        """
        Create a new server that acts like a homekit accessory.

        :param config_file: the file that contains the configuration data. Must be a string representing an absolute
        path to the file
        :param logger: this can be None to disable logging, sys.stderr to use the default behaviour of the python
        implementation or an instance of logging.Logger to use this.
        """
        if logger is None or logger == sys.stderr or isinstance(logger, logging.Logger):
            self.logger = logger
        else:
            raise Exception('Invalid logger given.')
        self.data = HomeKitServerData(config_file)
        self.data.increase_configuration_number()
        self.sessions = {}
        self.zeroconf = Zeroconf()
        self.mdns_type = '_hap._tcp.local.'
        self.mdns_name = self.data.name + '._hap._tcp.local.'

        self.accessories = Accessories()

        HTTPServer.__init__(self, (self.data.ip, self.data.port), HomeKitRequestHandler)

    def publish_device(self):
        desc = {'md': 'My Lightbulb',  # model name of accessory
                'ci': str(Categories['Lightbulb']),  # category identifier (page 254, 2 means bridge), must be a String
                'pv': '1.0',  # protocol version
                'c#': str(self.data.configuration_number),
                # configuration (consecutive number, 1 or greater, must be changed on every configuration change)
                'id': self.data.accessory_pairing_id_bytes,  # id MUST look like Mac Address
                'ff': '0',  # feature flags (Table 5-8, page 69)
                's#': '1',  # must be 1
                'sf': '1'  # status flag, lowest bit encodes pairing status, 1 means unpaired
                }
        if self.data.is_paired:
            desc['sf'] = '0'

        info = ServiceInfo(self.mdns_type, self.mdns_name, socket.inet_aton(self.data.ip), self.data.port, 0, 0, desc,
                           'ash-2.local.')
        self.zeroconf.unregister_all_services()
        self.zeroconf.register_service(info, allow_name_change=True)

    def unpublish_device(self):
        self.zeroconf.unregister_all_services()

    def shutdown(self):
        # tell all handlers to close the connection
        for session in self.sessions:
            self.sessions[session]['handler'].close_connection = True
        self.socket.close()
        HTTPServer.shutdown(self)
