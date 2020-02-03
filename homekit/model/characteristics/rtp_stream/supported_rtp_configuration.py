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

from enum import IntEnum
from homekit.model.characteristics import CharacteristicsTypes, CharacteristicFormats, CharacteristicPermissions, \
    AbstractCharacteristic
from homekit.protocol.tlv import TLVItem


class CameraSRTPCryptoSuite(IntEnum):
    AES_CM_128_HMAC_SHA1_80 = 0
    AES_256_CM_HMAC_SHA1_80 = 1
    DISABLED = 2


class SupportedRTPConfiguration:
    crypto_suite = TLVItem(2, CameraSRTPCryptoSuite)

    def __init__(self, crypto_suite):
        self.crypto_suite = crypto_suite


class SupportedRTPConfigurationCharacteristic(AbstractCharacteristic):
    """
    Defined on page 218
    """

    def __init__(self, iid, value):
        AbstractCharacteristic.__init__(self, iid, CharacteristicsTypes.SUPPORTED_RTP_CONFIGURATION,
                                        CharacteristicFormats.tlv8, SupportedRTPConfiguration)
        self.perms = [CharacteristicPermissions.paired_read]
        self.description = 'supported rtp configurations management service'
        self.value = value
