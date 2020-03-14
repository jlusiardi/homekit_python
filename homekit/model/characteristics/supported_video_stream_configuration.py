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

CHARACTERISTIC_ID = CharacteristicsTypes.get_uuid(CharacteristicsTypes.SUPPORTED_VIDEO_STREAM_CONFIGURATION)


class SupportedVideoStreamConfigurationKeys(IntEnum):
    """
    Page 219 / Table 9-25
    """
    VIDEO_CODEC_CONFIGURATION = 1


class VideoCodecConfigurationKeys(IntEnum):
    """
    Page 219 / Table 9-26
    """
    VIDEO_CODEC_TYPE = 1
    VIDEO_CODEC_PARAMETERS = 2
    VIDEO_ATTRIBUTES = 3


class VideoCodecTypeValues(IntEnum):
    """
    Page 219 / Table 9-26 value for 'Video Codec Type'
    """
    H264 = 0


class VideoCodecParametersKeys(IntEnum):
    """
    Page 220 / Table 9-27
    """
    PROFILE_ID = 1
    LEVEL = 2
    PACKETIZATION_MODE = 3
    CVO_ENABLED = 4
    CVO_ID = 5


class ProfileIdValues(IntEnum):
    """
    Page 220 / Table 9-27 Values for key 'ProfileID'
    """
    CONSTRAINED_BASELINE_PROFILE = 0
    MAIN_PROFILE = 1
    HIGH_PROFILE = 2


class LevelValues(IntEnum):
    """
    Page 220 / Table 9-27 Values for key 'Level'
    """
    L_3_1 = 0
    L_3_2 = 1
    L_4 = 2


class CVOEnabledValue(IntEnum):
    """
    Page 220 / Table 9-27 Values for key 'CVO Enabled'
    """
    NOT_SUPPORTED = 0
    SUPPORTED = 1


class PacketizationModeValues(IntEnum):
    """
    Page 220 / Table 9-27 Values for key 'Packetization mode'
    """
    NON_INTERLEAVED = 0


class VideoAttributesKeys(IntEnum):
    """
    Page 220 / Table 9-28
    """
    IMAGE_WIDTH = 1
    IMAGE_HEIGHT = 2
    FRAME_RATE = 3


def decoder(bytes_data):
    return tlv8.decode(bytes_data, {
        SupportedVideoStreamConfigurationKeys.VIDEO_CODEC_CONFIGURATION: {
            VideoCodecConfigurationKeys.VIDEO_CODEC_TYPE: VideoCodecTypeValues,
            VideoCodecConfigurationKeys.VIDEO_CODEC_PARAMETERS: {
                VideoCodecParametersKeys.PROFILE_ID: ProfileIdValues,
                VideoCodecParametersKeys.LEVEL: LevelValues,
                VideoCodecParametersKeys.PACKETIZATION_MODE: PacketizationModeValues,
                VideoCodecParametersKeys.CVO_ENABLED: PacketizationModeValues,
                VideoCodecParametersKeys.CVO_ID: tlv8.DataType.UNSIGNED_INTEGER
            },
            VideoCodecConfigurationKeys.VIDEO_ATTRIBUTES: {
                VideoAttributesKeys.IMAGE_WIDTH: tlv8.DataType.UNSIGNED_INTEGER,
                VideoAttributesKeys.IMAGE_HEIGHT: tlv8.DataType.UNSIGNED_INTEGER,
                VideoAttributesKeys.FRAME_RATE: tlv8.DataType.UNSIGNED_INTEGER,
            },
        }
    })
