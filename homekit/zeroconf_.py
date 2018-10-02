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


def get_from_properties(props, key, default=None, case_sensitive=True):
    """
    This function looks up the key in the given zeroconf service information properties. Those are a dict between bytes.
    The key to lookup is therefore also of type bytes.

    :param props: a dict from bytes to bytes.
    :param key: bytes as key
    :param default: the value to return, if the key was not found. Will be converted to str.
    :param case_sensitive: If this is False, try to lookup keys also when they only match ignoring their case
    :return: the value out of the dict as string (after decoding), the given default if the key was not not found but
             the default was given or None
    """
    if case_sensitive:
        tmp_props = props
        tmp_key = key
    else:
        tmp_props = {k.lower(): props[k] for k in props}
        tmp_key = key.lower()

    if tmp_key in tmp_props:
        return tmp_props[tmp_key].decode()
    else:
        if default:
            return str(default)


def discover_homekit_devices():
    zeroconf = Zeroconf()
    listener = CollectingListener()
    ServiceBrowser(zeroconf, '_hap._tcp.local.', listener)
    sleep(1)
    for info in listener.get_data():
        print('Name: {name}'.format(name=info.name))
        print('Url: http://{ip}:{port}'.format(ip=inet_ntoa(info.address), port=info.port))

        props = info.properties

        conf_number = get_from_properties(props, b'c#', case_sensitive=False)
        print('Configuration number (c#): {conf}'.format(conf=conf_number))

        flags = int(get_from_properties(props, b'ff', case_sensitive=False))
        print('Feature Flags (ff): {f} (Flag: {flags})'.format(f=FeatureFlags[flags], flags=flags))

        id = get_from_properties(props, b'id', case_sensitive=False)
        print('Device ID (id): {id}'.format(id=id))

        md = get_from_properties(props, b'md', case_sensitive=False)
        print('Model Name (md): {md}'.format(md=md))

        pv = get_from_properties(props, b'pv', case_sensitive=False, default='1.0 (default, not set in TXT record)')
        print('Protocol Version (pv): {pv}'.format(pv=pv))

        state_number = get_from_properties(props, b's#', case_sensitive=False)
        print('State Number (s#): {sn}'.format(sn=state_number))

        sf = get_from_properties(props, b'sf', case_sensitive=False)
        print('Status Flags (sf): {sf}'.format(sf=sf))

        ci = get_from_properties(props, b'ci', case_sensitive=False)
        print('Category Identifier (ci): {c} (Id: {ci})'.format(c=Categories[int(ci)], ci=ci))
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
