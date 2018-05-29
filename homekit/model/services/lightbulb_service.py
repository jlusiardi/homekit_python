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

from homekit.model import get_id
from homekit.model.characteristics.on import OnCharacteristicMixin
from homekit.model.services import ServicesTypes, AbstractService


class LightBulbService(AbstractService, OnCharacteristicMixin):
    """
    Defined on page 217
    """

    def __init__(self):
        AbstractService.__init__(self, ServicesTypes.get_uuid('public.hap.service.lightbulb'), get_id())
        OnCharacteristicMixin.__init__(self, get_id())
