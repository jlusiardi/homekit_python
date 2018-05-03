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

from socket import inet_ntoa
from time import sleep
from zeroconf import ServiceBrowser, Zeroconf

from homekit.feature_flags import FeatureFlags
from homekit.model.categories import Categories


class CollectingListener(object):
    def __init__(self):
        self.data = []

    def remove_service(self, zeroconf, type, name):
        # this is ignored since not interested in disappearing stuff
        pass

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        self.data.append(info)

    def get_data(self):
        return self.data


def discover_homekit_devices():
    zeroconf = Zeroconf()
    listener = CollectingListener()
    ServiceBrowser(zeroconf, '_hap._tcp.local.', listener)
    sleep(1)
    for info in listener.get_data():
        print('Name: {name}'.format(name=info.name))
        print('Url: http://{ip}:{port}'.format(ip=inet_ntoa(info.address), port=info.port))
        print('Configuration number (c#): {conf}'.format(conf=info.properties[b'c#'].decode()))
        flags = int(info.properties[b'ff'].decode())
        print('Feature Flags (ff): {f} (Flag: {flags})'.format(f=FeatureFlags[flags], flags=flags))
        print('Device ID (id): {id}'.format(id=info.properties[b'id'].decode()))
        print('Model Name (md): {md}'.format(md=info.properties[b'md'].decode()))
        if b'pv' in info.properties:
            print('Protocol Version (pv): {pv}'.format(pv=info.properties[b'pv'].decode()))
        else:
            print('Protocol Version (pv): 1.0 (default, not set in TXT record)')
        print('State Number (s#): {sn}'.format(sn=info.properties[b's#'].decode()))
        print('Status Flags (sf): {sf}'.format(sf=info.properties[b'sf'].decode()))
        category = int(info.properties[b'ci'].decode())
        print('Category Identifier (ci): {c} (Id: {ci})'.format(c=Categories[category], ci=category))
        print()

    zeroconf.close()


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
