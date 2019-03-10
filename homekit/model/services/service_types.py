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


class _ServicesTypes(object):
    """
    This data is taken from chapter 9 page 216 onwards.
    """
    INFORMATION_SERVICE = 'A2'  # new for ble, homekit spec page 126
    PAIRING_SERVICE = '55'      # new for ble, homekit spec page 57
    ACCESSORY_INFORMATION_SERVICE = '3E'
    BATTERY_SERVICE = '96'

    def __init__(self):
        self.baseUUID = '-0000-1000-8000-0026BB765291'
        self._services = {
            '3E': 'public.hap.service.accessory-information',
            '40': 'public.hap.service.fan',
            '41': 'public.hap.service.garage-door-opener',
            '43': 'public.hap.service.lightbulb',
            '44': 'public.hap.service.lock-management',
            '45': 'public.hap.service.lock-mechanism',
            '47': 'public.hap.service.outlet',
            '49': 'public.hap.service.switch',
            '4A': 'public.hap.service.thermostat',
            '55': 'public.hap.service.pairing',                             # new for ble, homekit spec page 57
            '7E': 'public.hap.service.security-system',
            '7F': 'public.hap.service.sensor.carbon-monoxide',
            '80': 'public.hap.service.sensor.contact',
            '81': 'public.hap.service.door',
            '82': 'public.hap.service.sensor.humidity',
            '83': 'public.hap.service.sensor.leak',
            '84': 'public.hap.service.sensor.light',
            '85': 'public.hap.service.sensor.motion',
            '86': 'public.hap.service.sensor.occupancy',
            '87': 'public.hap.service.sensor.smoke',
            '89': 'public.hap.service.stateless-programmable-switch',
            '8A': 'public.hap.service.sensor.temperature',
            '8B': 'public.hap.service.window',
            '8C': 'public.hap.service.window-covering',
            '8D': 'public.hap.service.sensor.air-quality',
            '96': 'public.hap.service.battery',
            '97': 'public.hap.service.sensor.carbon-dioxide',
            'A2': 'public.hap.service.protocol.information.service',        # new for ble, homekit spec page 126
            'B7': 'public.hap.service.fanv2',
            'B9': 'public.hap.service.vertical-slat',
            'BA': 'public.hap.service.filter-maintenance',
            'BB': 'public.hap.service.air-purifier',
            'CC': 'public.hap.service.service-label',
            '110': 'public.hap.service.camera-rtp-stream-management',
            '112': 'public.hap.service.microphone',
            '113': 'public.hap.service.speaker',
            '121': 'public.hap.service.doorbell',
        }

        self._services_rev = {self._services[k]: k for k in self._services.keys()}

    def __getitem__(self, item):
        if item in self._services:
            return self._services[item]

        if item in self._services_rev:
            return self._services_rev[item]

        # raise KeyError('Item {item} not found'.format_map(item=item))
        return 'Unknown Service: {i}'.format(i=item)

    def get_short(self, item):
        """
        get the short version of the service name (aka the last segment of the name) or if this is not in the list of
        services it returns 'Unknown Service: XX'.

        :param item: the items full UUID
        :return: the last segment of the service name or a hint that it is unknown
        """
        orig_item = item
        item = item.upper()
        if item.endswith(self.baseUUID):
            item = item.split('-', 1)[0]
            item = item.lstrip('0')

        if item in self._services:
            return self._services[item].split('.')[-1]
        return 'Unknown Service: {i}'.format(i=orig_item)

    def get_uuid(self, item_name):
        """
        Returns the full length UUID for either a shorted UUID or textual characteristic type name. For information on
        full and short UUID consult chapter 5.6.1 page 72 of the specification. It also supports to pass through full
        HomeKit UUIDs.

        :param item_name: either the type name (e.g. "public.hap.characteristic.position.current") or the short UUID or
                          a HomeKit specific full UUID.
        :return: the full UUID (e.g. "0000006D-0000-1000-8000-0026BB765291")
        :raises KeyError: if the input is neither a short UUID nor a type name. Specific error is given in the message.
        """
        orig_item = item_name
        # if we get a full length uuid with the proper base and a known short one, this should also work.
        if item_name.upper().endswith(self.baseUUID):
            item_name = item_name.upper()
            item_name = item_name.split('-', 1)[0]
            item_name = item_name.lstrip('0')

        if item_name.lower() in self._services_rev:
            short = self._services_rev[item_name.lower()]
        elif item_name.upper() in self._services:
            short = item_name.upper()
        else:
            raise KeyError('No UUID found for Item {item}'.format(item=orig_item))

        medium = '0' * (8 - len(short)) + short
        long = medium + self.baseUUID
        return long


#
#   Have a singleton to avoid overhead
#
ServicesTypes = _ServicesTypes()
