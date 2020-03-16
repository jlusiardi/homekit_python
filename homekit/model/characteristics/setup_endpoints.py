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
from homekit.model.characteristics.characteristic_types import CharacteristicsTypes

CHARACTERISTIC_ID = CharacteristicsTypes.get_uuid(CharacteristicsTypes.SETUP_ENDPOINTS)


class CameraSRTPCryptoSuiteValues(IntEnum):
    """
    Page 218 / Table 9-24 Values for key 'SRTP Crypto Suite'
    Page 209 / Table 9-15 Values for key 'SRTP Crypto Suite'
    """
    AES_CM_128_HMAC_SHA1_80 = 0
    AES_256_CM_HMAC_SHA1_80 = 1
    DISABLED = 2


class SrtpParameterKeys(IntEnum):
    """
    Page 209 / Table 9-15
    """
    SRTP_CRYPTO_SUITE = 1
    SRTP_MASTER_KEY = 2
    SRTP_MASTER_SALT = 3


class SetupEndpointsKeys(IntEnum):
    """
    Page 208 / Table 9-13
    Page 210 / Table 9-16
    """
    SESSION_ID = 1
    STATUS = 2
    ADDRESS = 3
    SRTP_PARAMETERS_FOR_VIDEO = 4
    SRTP_PARAMETERS_FOR_AUDIO = 5
    VIDEO_RTP_SSRC = 6
    AUDIO_RTP_SSRC = 7


class EndpointStatusValues(IntEnum):
    """
    Page 210 / Table 9-16 Values for key status
    """
    SUCCESS = 0
    BUSY = 1
    ERROR = 2


class IPVersionValues(IntEnum):
    """
    Page 208 / Table 9-14 values for key 'IP address version'
    """
    IPV4 = 0
    IPV6 = 1


class ControllerAddressKeys(IntEnum):
    """
    Page 208 / Table 9-14
    """
    IP_ADDRESS_VERSION = 1
    IP_ADDRESS = 2
    VIDEO_RTP_PORT = 3
    AUDIO_RTP_PORT = 4


def decoder(bytes_data):
    srtp_params = {
        SrtpParameterKeys.SRTP_CRYPTO_SUITE: CameraSRTPCryptoSuiteValues,
        SrtpParameterKeys.SRTP_MASTER_KEY: tlv8.DataType.BYTES,
        SrtpParameterKeys.SRTP_MASTER_SALT: tlv8.DataType.BYTES,
    }
    return tlv8.decode(bytes_data, {
        SetupEndpointsKeys.SESSION_ID: tlv8.DataType.BYTES,
        SetupEndpointsKeys.STATUS: EndpointStatusValues,
        SetupEndpointsKeys.ADDRESS: {
            ControllerAddressKeys.IP_ADDRESS_VERSION: IPVersionValues,
            ControllerAddressKeys.IP_ADDRESS: tlv8.DataType.STRING,
            ControllerAddressKeys.VIDEO_RTP_PORT: tlv8.DataType.UNSIGNED_INTEGER,
            ControllerAddressKeys.AUDIO_RTP_PORT: tlv8.DataType.UNSIGNED_INTEGER,
        },
        SetupEndpointsKeys.SRTP_PARAMETERS_FOR_VIDEO: srtp_params,
        SetupEndpointsKeys.SRTP_PARAMETERS_FOR_AUDIO: srtp_params,
        SetupEndpointsKeys.VIDEO_RTP_SSRC: tlv8.DataType.BYTES,
        SetupEndpointsKeys.AUDIO_RTP_SSRC: tlv8.DataType.BYTES,
    })
