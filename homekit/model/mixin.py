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
