import json

id_counter = 0


def get_id():
    global id_counter
    id_counter += 1
    return id_counter


class ToDictMixin(object):
    """
    Will help to convert the various accessories, services and characteristics to JSON.
    """

    def _to_dict(self):
        tmp = {}
        for x in dir(self):
            if x.startswith('_') or callable(getattr(self, x)):
                continue
            val = getattr(self, x)
            if val is None:
                continue
            if isinstance(val, list):
                tmpval = []
                for e in val:
                    if isinstance(e, str):
                        tmpval.append(e)
                    else:
                        tmpval.append(e._to_dict())
                tmp[x] = tmpval
            else:
                tmp[x] = val

        return tmp

    def __str__(self):
        d = self._to_dict()
        return json.dumps(d)
