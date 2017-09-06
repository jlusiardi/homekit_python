from http.server import HTTPServer
from socketserver import ThreadingMixIn
from zeroconf import Zeroconf, ServiceInfo
import socket

from homekit.serverdata import HomeKitServerData
from homekit.request_handler import HomeKitRequestHandler
from homekit.model import Accessories, Categories


class HomeKitServer(ThreadingMixIn, HTTPServer):
    def __init__(self, data_file):
        self.data = HomeKitServerData(data_file)
        self.data.increase_configuration_number()
        self.sessions = {}
        self.zeroconf = Zeroconf()
        self.mdns_type = '_hap._tcp.local.'
        self.mdns_name = self.data.name + '._hap._tcp.local.'

        self.accessories = Accessories()

        # accessory = homekit.model.Accessory(1, 'me')
        # accessory.services.append(homekit.model.LightBulbService(2, 'light'))
        # self.accessories.add_accessory(accessory)
        HTTPServer.__init__(self, (self.data.ip, self.data.port), HomeKitRequestHandler)

    def publish_device(self):
        desc = {'md': 'My Lightbulb',  # model name of accessory
                'ci': Categories['Lightbulb'],  # category identifier (page 254, 2 means bridge)
                'pv': '1.0',  # protocol version
                'c#': str(self.data.configuration_number),
                # configuration (consecutive number, 1 or greater, must be changed on every configuration change)
                'id': self.data.accessory_pairing_id_bytes,  # id MUST look like Mac Address
                'ff': '0',  # feature flags
                's#': '1',  # must be 1
                'sf': '1'  # status flag, lowest bit encodes pairing status, 1 means unpaired
                }
        if self.data.is_paired:
            desc['sf'] = '0'

        info = ServiceInfo(self.mdns_type, self.mdns_name, socket.inet_aton(self.data.ip), self.data.port, 0, 0, desc,
                           'ash-2.local.')
        self.zeroconf.unregister_all_services()
        self.zeroconf.register_service(info)

    def unpublish_device(self):
        self.zeroconf.unregister_all_services()
