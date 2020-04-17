#
# Copyright 2020 Joachim Lusiardi
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
from homekit.model.characteristics.setup_endpoints import CameraSRTPCryptoSuiteValues


class SupportedSrtpConfigurationKeys(IntEnum):
    """
    Page 218 / Table 9-24
    """
    SRTP_CRYPTO_SUITE = 2


def decoder(bytes_data):
    return tlv8.decode(bytes_data, {
        SupportedSrtpConfigurationKeys.SRTP_CRYPTO_SUITE: CameraSRTPCryptoSuiteValues
    })
