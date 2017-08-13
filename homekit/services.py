class _ServicesTypes(object):
    """
    This data is taken from Table 12-3 Accessory Categories on page 254. Values above 19 are reserved.
    """

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
        orig_item = item
        if item.endswith(self.baseUUID):
            item = item.split('-', 1)[0]
            item = item.lstrip('0')

        if item in self._services:
            return self._services[item].split('.')[-1]
        return 'Unknown Service: {i}'.format(i=orig_item)


ServicesTypes = _ServicesTypes()
