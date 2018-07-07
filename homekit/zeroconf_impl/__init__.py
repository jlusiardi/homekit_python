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

from _socket import inet_ntoa
from time import sleep

from zeroconf import Zeroconf, ServiceBrowser

from homekit.model import Categories
from homekit.model.feature_flags import FeatureFlags


class CollectingListener(object):
    def __init__(self):
        self.data = []

    def remove_service(self, zeroconf, type, name):
        # this is ignored since not interested in disappearing stuff
        pass

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info is not None:
            self.data.append(info)

    def get_data(self):
        return self.data


def discover_homekit_devices(max_seconds=10):
    zeroconf = Zeroconf()
    listener = CollectingListener()
    ServiceBrowser(zeroconf, '_hap._tcp.local.', listener)
    sleep(max_seconds)
    tmp = []
    for info in listener.get_data():
        d = {}
        tmp.append(d)

        # from Bonjour discovery
        d['name'] = info.name
        d['address'] = inet_ntoa(info.address)
        d['port'] = info.port

        # stuff taken from the Bonjour TXT record (see table 5-7 on page 69)
        flags = int(info.properties[b'ff'].decode())
        category = int(info.properties[b'ci'].decode())
        d['c#'] = info.properties[b'c#'].decode()

        d['ff'] = flags
        d['flags'] = FeatureFlags[flags]

        d['id'] = info.properties[b'id'].decode()

        d['md'] = info.properties[b'md'].decode()

        if b'pv' in info.properties:
            d['pv'] = info.properties[b'pv'].decode()
        else:
            d['pv'] = '1.0'

        d['s#'] = info.properties[b's#'].decode()

        d['sf'] = info.properties[b'sf'].decode()

        d['ci'] = category
        d['category'] = Categories[category]

    zeroconf.close()
    return tmp


def find_device_ip_and_port(device_id: str):
    result = None
    zeroconf = Zeroconf()
    listener = CollectingListener()
    ServiceBrowser(zeroconf, '_hap._tcp.local.', listener)
    counter = 0

    while result is None and counter < 10:
        sleep(2)
        data = listener.get_data()
        for info in data:
            if info.properties[b'id'].decode() == device_id:
                result = {'ip': inet_ntoa(info.address), 'port': info.port}
                break
        counter += 1

    zeroconf.close()
    return result
