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

CHARACTERISTIC_ID = CharacteristicsTypes.get_uuid(CharacteristicsTypes.SUPPORTED_AUDIO_CONFIGURATION)


class SupportedAudioStreamConfigurationKeys(IntEnum):
    """
    Page 215 / Table 9-18
    """
    AUDIO_CODEC_CONFIGURATION = 1
    COMFORT_NOISE_SUPPORT = 2


class AudioCodecConfigurationKeys(IntEnum):
    """
    Page 215 / Table 9-18
    """
    CODEC_TYPE = 1
    AUDIO_CODEC_PARAMETERS = 2


class AudioCodecTypeValues(IntEnum):
    """
    Page 207 / Table 9-11 Values for key 'Selected Audio Codec type'
    """
    AAC_ELD = 2
    OPUS = 3
    AMR = 5
    AMR_WB = 6


class AudioCodecParametersKeys(IntEnum):
    """
    Page 217 / Table 9-21
    """
    AUDIO_CHANNELS = 1
    BIT_RATE = 2
    SAMPLE_RATE = 3
    RTP_TIME = 4


class BitRateValues(IntEnum):
    """
    Page 217 / Table 9-21 values for key 'Bit-rate'
    """
    VARIABLE = 0
    CONSTANT = 1


class SampleRateValues(IntEnum):
    """
    Page 217 / Table 9-21 values for key 'Sample rate'
    """
    KHZ_8 = 0
    KHZ_16 = 1
    KHZ_24 = 2


class RtpTimeValues(IntEnum):
    """
    Page 217 / Table 9-21 values for key 'RTP Time'
    """
    _20_MS = 20
    _30_MS = 30
    _40_MS = 40
    _60_MS = 60


def decoder(bytes_data):
    return tlv8.decode(bytes_data, {
        SupportedAudioStreamConfigurationKeys.AUDIO_CODEC_CONFIGURATION: {
            AudioCodecConfigurationKeys.CODEC_TYPE: AudioCodecTypeValues,
            AudioCodecConfigurationKeys.AUDIO_CODEC_PARAMETERS: {
                AudioCodecParametersKeys.AUDIO_CHANNELS: tlv8.DataType.UNSIGNED_INTEGER,
                AudioCodecParametersKeys.BIT_RATE: BitRateValues,
                AudioCodecParametersKeys.SAMPLE_RATE: SampleRateValues,
                AudioCodecParametersKeys.RTP_TIME: RtpTimeValues
            }
        },
        SupportedAudioStreamConfigurationKeys.COMFORT_NOISE_SUPPORT: tlv8.DataType.UNSIGNED_INTEGER
    })
