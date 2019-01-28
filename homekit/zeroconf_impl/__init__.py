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
from homekit.model.status_flags import StatusFlags


class CollectingListener(object):
    """
    Helper class to collect all zeroconf announcements.
    """
    def __init__(self):
        self.data = []

    def remove_service(self, zeroconf, zeroconf_type, name):
        # this is ignored since not interested in disappearing stuff
        pass

    def add_service(self, zeroconf, zeroconf_type, name):
        info = zeroconf.get_service_info(zeroconf_type, name)
        if info is not None:
            self.data.append(info)

    def get_data(self):
        """
        Use this method to get the data of the collected announcements.

        :return: a List of zeroconf.ServiceInfo instances
        """
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


def discover_homekit_devices(max_seconds=10):
    """
    This method discovers all HomeKit Accessories. It browses for devices in the _hap._tcp.local. domain and checks if
    all required fields are set in the text record. It one field is missing, it will be excluded from the result list.

    :param max_seconds: the number of seconds we will wait for the devices to be discovered
    :return: a list of dicts containing all fields as described in table 5.7 page 69
    """
    zeroconf = Zeroconf()
    listener = CollectingListener()
    ServiceBrowser(zeroconf, '_hap._tcp.local.', listener)
    sleep(max_seconds)
    tmp = []
    for info in listener.get_data():
        # from Bonjour discovery
        d = {
            'name': info.name,
            'address': inet_ntoa(info.address),
            'port': info.port
        }

        props = info.properties

        # stuff taken from the Bonjour TXT record (see table 5-7 on page 69)
        conf_number = get_from_properties(props, b'c#', case_sensitive=False)
        if conf_number:
            d['c#'] = conf_number
        else:
            continue

        ff = get_from_properties(props, b'ff', case_sensitive=False)
        if ff:
            flags = int(ff)
        else:
            flags = 0
        d['ff'] = flags
        d['flags'] = FeatureFlags[flags]

        id = get_from_properties(props, b'id', case_sensitive=False)
        if id:
            d['id'] = id

        md = get_from_properties(props, b'md', case_sensitive=False)
        if md:
            d['md'] = md
        else:
            continue

        pv = get_from_properties(props, b'pv', case_sensitive=False, default='1.0')
        if pv:
            d['pv'] = pv

        s = get_from_properties(props, b's#', case_sensitive=False)
        if s:
            d['s#'] = s

        sf = get_from_properties(props, b'sf', case_sensitive=False)
        if sf:
            d['sf'] = sf
        d['statusflags'] = StatusFlags[int(sf)]

        ci = get_from_properties(props, b'ci', case_sensitive=False)
        if ci:
            category = info.properties[b'ci'].decode()
            d['ci'] = category
            d['category'] = Categories[int(category)]

        # append device, it has all data
        tmp.append(d)

    zeroconf.close()
    return tmp


def find_device_ip_and_port(device_id: str, max_seconds=10):
    """
    Try to find a HomeKit Accessory via Bonjour. The process is time boxed by the second parameter which sets an upper
    limit of `max_seconds` before it times out. The runtime of the function may be longer because of the Bonjour handling
    code.

    :param device_id: the Accessory's pairing id
    :param max_seconds: the number of seconds to wait for the accessory to be found
    :return: a dict with ip and port if the accessory was found or None
    """
    result = None
    zeroconf = Zeroconf()
    listener = CollectingListener()
    ServiceBrowser(zeroconf, '_hap._tcp.local.', listener)
    counter = 0

    while result is None and counter < max_seconds:
        sleep(1)
        data = listener.get_data()
        for info in data:
            if info.properties[b'id'].decode() == device_id:
                result = {'ip': inet_ntoa(info.address), 'port': info.port}
                break
        counter += 1

    zeroconf.close()
    return result
