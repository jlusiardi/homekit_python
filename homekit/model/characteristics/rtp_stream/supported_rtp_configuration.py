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

import tlv8
from enum import IntEnum
from homekit.model.characteristics import CharacteristicsTypes, CharacteristicFormats, CharacteristicPermissions, \
    AbstractCharacteristic


class SupportedRtpConfigurationKeys:
    """
    Page 218 / Table 9-24
    """
    SRTP_CRYPTO_SUITE = 2


class CameraSRTPCryptoSuite(IntEnum):
    """
    Page 218 / Table 9-24 Values for key 'SRTP Crypto Suite'
    Page 209 / Table 9-15 Values for key 'SRTP Crypto Suite'
    """
    AES_CM_128_HMAC_SHA1_80 = 0
    AES_256_CM_HMAC_SHA1_80 = 1
    DISABLED = 2


class SupportedRTPConfiguration:
    """
    Page 218 / Table 9-24
    """
    def __init__(self, crypto_suites):
        self.crypto_suites = crypto_suites

    def to_entry_list(self):
        entryList = tlv8.EntryList()
        for suite in self.crypto_suites:
            entryList.append(tlv8.Entry(2, suite))
        return entryList


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
