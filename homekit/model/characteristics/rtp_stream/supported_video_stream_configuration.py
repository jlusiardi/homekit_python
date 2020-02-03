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


class H264Profile(IntEnum):
    CONSTRAINED_BASELINE_PROFILE = 0
    MAIN_PROFILE = 1
    HIGH_PROFILE = 2


class H264Level(IntEnum):
    L_3_1 = 0
    L_3_2 = 1
    L_4 = 2


class VideoCodecType(IntEnum):
    H264 = 0


class PacketizationMode(IntEnum):
    NON_INTERLEAVED = 0


class CVOEnabled(IntEnum):
    NOT_SUPPORTED = 0
    SUPPORTED = 1


class VideoCodecParameters:
    profile = TLVItem(1, H264Profile)
    level = TLVItem(2, H264Level)
    packetization_mode = TLVItem(3, PacketizationMode)
    cvo_enabled = TLVItem(4, CVOEnabled)

    def __init__(self, profile, level, packetization_mode=PacketizationMode.NON_INTERLEAVED,
                 cvo_enabled=CVOEnabled.NOT_SUPPORTED):
        self.profile = profile
        self.level = level
        self.packetization_mode = packetization_mode
        self.cvo_enabled = cvo_enabled


class VideoAttributes:
    width = TLVItem(1, int)
    height = TLVItem(2, int)
    frame_rate = TLVItem(3, int)

    def __init__(self, width, height, frame_rate):
        self.width = width
        self.height = height
        self.frame_rate = frame_rate


class VideoCodecConfiguration:
    codec_type = TLVItem(1, VideoCodecType)
    codec_parameters = TLVItem(2, VideoCodecParameters)
    attributes = TLVItem(3, VideoAttributes)

    def __init__(self, codec_parameters, attributes, codec_type=VideoCodecType.H264):
        self.codec_type = codec_type
        self.codec_parameters = codec_parameters
        self.attributes = attributes


class SupportedVideoStreamConfiguration:
    config = TLVItem(1, VideoCodecConfiguration)

    def __init__(self, config):
        self.config = config


class SupportedVideoStreamConfigurationCharacteristic(AbstractCharacteristic):
    """
    Defined on page 219
    """

    def __init__(self, iid, value):
        AbstractCharacteristic.__init__(self, iid, CharacteristicsTypes.SUPPORTED_VIDEO_STREAM_CONFIGURATION,
                                        CharacteristicFormats.tlv8, SupportedVideoStreamConfiguration)
        self.perms = [CharacteristicPermissions.paired_read]
        self.description = 'parameters supported for streaming video over an RTP session'
        self.value = value
