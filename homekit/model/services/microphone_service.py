#
# Copyright 2019 Christoph Walcher
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
from homekit.model.characteristics import MicrophoneMuteCharacteristicMixin
from homekit.model.services import ServicesTypes, AbstractService


class MicrophoneService(AbstractService, MicrophoneMuteCharacteristicMixin):
    """
    Defined on page 149; Used to mute a microphone
    """

    def __init__(self):
        AbstractService.__init__(self, ServicesTypes.get_uuid('public.hap.service.microphone'), get_id())
        MicrophoneMuteCharacteristicMixin.__init__(self, get_id())
