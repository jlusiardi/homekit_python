class _FeatureFlags(object):
    """
    Data taken form table 5-8 Bonjour TXT Record Feature Flags on page 69.
    """

    def __init__(self):
        self._data = {
            0: 'Paired',
            1: 'Supports Pairing'
        }

    def __getitem__(self, item):
        if item in self._data:
            return self._data[item]

        raise KeyError('Item {item} not found'.format_map(item=item))


FeatureFlags = _FeatureFlags()
