class _ServicesTypes(object):
    """
    This data is taken from Table 12-3 Accessory Categories on page 254. Values above 19 are reserved.
    """

    def __init__(self):
        self.baseUUID = '-0000-1000-8000-0026BB765291'
        self._services = {
            '3E': 'public.hap.service.accessory-information',
            '47': 'public.hap.service.outlet'
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
        if item in self._services:
            return self._services[item].split('.')[-1]
        return 'Unknown Service: {i}'.format(i=item)


ServicesTypes = _ServicesTypes()
