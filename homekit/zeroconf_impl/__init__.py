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

from time import sleep
import logging
from zeroconf import Zeroconf, ServiceBrowser
from _socket import inet_ntoa


from homekit.model import Categories
from homekit.model.feature_flags import FeatureFlags
from homekit.model.status_flags import IpStatusFlags


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

    def update_service(self, zeroconf, service_type, name, state_change):
        # prevent FutureWarning: XXX has no update_service method. Provide one
        # (it can be empty if you don't care about the updates), it'll become
        # mandatory.
        logging.debug(
            'update_service zeroconf=%s service_type=%s name=%s state_change=%s',
            zeroconf,
            service_type,
            name,
            state_change,
        )


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
        return tmp_props[tmp_key]
    else:
        if default:
            return str(default)
    return None


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
        data = {
            'name': info.name,
            'address': inet_ntoa(info.addresses[0]),
            'port': info.port
        }

        logging.debug('candidate data %s', info.properties)

        data.update(parse_discovery_properties(decode_discovery_properties(
            info.properties
        )))

        if 'c#' not in data or 'md' not in data:
            continue
        logging.debug('found Homekit IP accessory %s', data)
        tmp.append(data)

    zeroconf.close()
    return tmp


def decode_discovery_properties(props):
    """
    This method decodes unicode bytes in _hap._tcp Bonjour TXT record keys to python strings.

    :params: a dictionary of key/value TXT records from Bonjour discovery. These are assumed
    to be bytes type.
    :return: A dictionary of key/value TXT records from Bonjour discovery. These are now str.
    """
    out = {}
    for k, value in props.items():
        out[k.decode('utf-8')] = value.decode('utf-8')
    return out


def parse_discovery_properties(props):
    """
    This method normalizes and parses _hap._tcp Bonjour TXT record keys.

    This is done automatically if you are using the discovery features built in to the library. If you are
    integrating into an existing system it may already do its own Bonjour discovery. In that case you can
    call this function to normalize the properties it has discovered.

    :param props: a dictionary of key/value TXT records from doing Bonjour discovery. These should be
    decoded as strings already. Byte data should be decoded with decode_discovery_properties.
    :return: A dictionary contained the parsed and normalized data.
    """
    data = {}

    # stuff taken from the Bonjour TXT record (see table 5-7 on page 69)
    conf_number = get_from_properties(props, 'c#', case_sensitive=False)
    if conf_number:
        data['c#'] = conf_number

    feature_flags = get_from_properties(props, 'ff', case_sensitive=False)
    if feature_flags:
        flags = int(feature_flags)
    else:
        flags = 0
    data['ff'] = flags
    data['flags'] = FeatureFlags[flags]

    dev_id = get_from_properties(props, 'id', case_sensitive=False)
    if dev_id:
        data['id'] = dev_id

    model_name = get_from_properties(props, 'md', case_sensitive=False)
    if model_name:
        data['md'] = model_name

    protocol_version = get_from_properties(props, 'pv', case_sensitive=False, default='1.0')
    if protocol_version:
        data['pv'] = protocol_version

    status = get_from_properties(props, 's#', case_sensitive=False)
    if status:
        data['s#'] = status

    status_flag = get_from_properties(props, 'sf', case_sensitive=False)
    if status_flag:
        data['sf'] = status_flag
        data['statusflags'] = IpStatusFlags[int(status_flag)]

    category_id = get_from_properties(props, 'ci', case_sensitive=False)
    if category_id:
        category = props['ci']
        data['ci'] = category
        data['category'] = Categories[int(category)]

    return data


def find_device_ip_and_port(device_id: str, max_seconds=10):
    """
    Try to find a HomeKit Accessory via Bonjour. The process is time boxed by the second parameter which sets an upper
    limit of `max_seconds` before it times out. The runtime of the function may be longer because of the Bonjour
    handling code.

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
                result = {'ip': inet_ntoa(info.addresses[0]), 'port': info.port}
                break
        counter += 1

    zeroconf.close()
    return result
