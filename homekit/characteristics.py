class _CharacteristicsTypes(object):
    """
    This data is taken from Table 12-3 Accessory Categories on page 254. Values above 19 are reserved.
    """

    def __init__(self):
        self.baseUUID = '-0000-1000-8000-0026BB765291'
        self._characteristics = {
            '14': 'public.hap.characteristic.identify',
            '20': 'public.hap.characteristic.manufacturer',
            '21': 'public.hap.characteristic.model',
            '23': 'public.hap.characteristic.name',
            '25': 'public.hap.characteristic.on',
            '26': 'public.hap.characteristic.outlet-in-use',
            '30': 'public.hap.characteristic.serial-number',
            '52': 'public.hap.characteristic.firmware.revision'
        }

        self._characteristics_rev = {self._characteristics[k]: k for k in self._characteristics.keys()}

    def __getitem__(self, item):
        if item in self._characteristics:
            return self._characteristics[item]

        if item in self._characteristics_rev:
            return self._characteristics_rev[item]

        # raise KeyError('Item {item} not found'.format_map(item=item))
        return 'Unknown Characteristic {i}?'.format(i=item)

    def get_short(self, item):
        if item in self._characteristics:
            return self._characteristics[item].split('.')[-1]
        return 'Unknown Characteristic {i}?'.format(i=item)


CharacteristicsTypes = _CharacteristicsTypes()
