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


class H264Profile(IntEnum):
    """
    Page 220 / Table 9-27 Values for key 'ProfileID'
    """
    CONSTRAINED_BASELINE_PROFILE = 0
    MAIN_PROFILE = 1
    HIGH_PROFILE = 2


class H264Level(IntEnum):
    """
    Page 220 / Table 9-27 Values for key 'Level'
    """
    L_3_1 = 0
    L_3_2 = 1
    L_4 = 2


class VideoCodecType(IntEnum):
    """
    Page 219 / Table 9-26 value for 'Video Codec Type'
    """
    H264 = 0


class PacketizationMode(IntEnum):
    """
    Page 220 / Table 9-27 Values for key 'Packetization mode'
    """
    NON_INTERLEAVED = 0


class CVOEnabled(IntEnum):
    """
    Page 220 / Table 9-27 Values for key 'CVO Enabled'
    """
    NOT_SUPPORTED = 0
    SUPPORTED = 1


class VideoCodecParametersKeys(IntEnum):
    """
    Page 220 / Table 9-27
    """
    PROFILE_ID = 1
    LEVEL = 2
    PACKETIZATION_MODE = 3
    CVO_ENABLED = 4
    CVO_ID = 5


class VideoCodecParameters:
    """
    Page 220 / Table 9-27
    """

    def __init__(self,
                 profile: H264Profile,
                 level: H264Level,
                 packetization_mode: PacketizationMode,
                 cvo_enabled: CVOEnabled):
        self.profile = profile
        self.level = level
        self.packetization_mode = packetization_mode
        self.cvo_enabled = cvo_enabled

    def to_entry_list(self):
        return tlv8.EntryList([
            tlv8.Entry(VideoCodecParametersKeys.PROFILE_ID, self.profile),
            tlv8.Entry(VideoCodecParametersKeys.LEVEL, self.level),
            tlv8.Entry(VideoCodecParametersKeys.PACKETIZATION_MODE, self.packetization_mode),
            tlv8.Entry(VideoCodecParametersKeys.CVO_ENABLED, self.cvo_enabled),
        ])

    @staticmethod
    def parse(source_bytes):
        data_format = {
            VideoCodecParametersKeys.PROFILE_ID: H264Profile,
            VideoCodecParametersKeys.LEVEL: H264Level,
            VideoCodecParametersKeys.PACKETIZATION_MODE: PacketizationMode,
            VideoCodecParametersKeys.CVO_ENABLED: CVOEnabled,
        }
        el = tlv8.decode(source_bytes, data_format)
        return el

    @staticmethod
    def from_entry_list(data: tlv8.EntryList):
        profile = data.first_by_id(VideoCodecParametersKeys.PROFILE_ID).data
        level = data.first_by_id(VideoCodecParametersKeys.LEVEL).data
        mode = data.first_by_id(VideoCodecParametersKeys.PACKETIZATION_MODE).data
        cvo = data.first_by_id(VideoCodecParametersKeys.CVO_ENABLED).data
        return VideoCodecParameters(profile, level, mode, cvo)


class VideoAttributesKeys(IntEnum):
    """
    Page 220 / Table 9-28
    """
    IMAGE_WIDTH = 1
    IMAGE_HEIGHT = 2
    FRAME_RATE = 3


class VideoAttributes:
    """
    Page 220 / Table 9-28
    """

    def __init__(self, width, height, frame_rate):
        self.width = width
        self.height = height
        self.frame_rate = frame_rate

    def to_entry_list(self):
        return tlv8.EntryList([
            tlv8.Entry(VideoAttributesKeys.IMAGE_WIDTH, self.width),
            tlv8.Entry(VideoAttributesKeys.IMAGE_HEIGHT, self.height),
            tlv8.Entry(VideoAttributesKeys.FRAME_RATE, self.frame_rate),
        ])

    @staticmethod
    def parse(source_bytes):
        data_format = {
            VideoAttributesKeys.IMAGE_WIDTH: tlv8.DataType.INTEGER,
            VideoAttributesKeys.IMAGE_HEIGHT: tlv8.DataType.INTEGER,
            VideoAttributesKeys.FRAME_RATE: tlv8.DataType.INTEGER,
        }
        el = tlv8.decode(source_bytes, data_format)
        return el

    @staticmethod
    def from_entry_list(data: tlv8.EntryList):
        width = data.first_by_id(VideoAttributesKeys.IMAGE_WIDTH).data
        height = data.first_by_id(VideoAttributesKeys.IMAGE_HEIGHT).data
        rate = data.first_by_id(VideoAttributesKeys.FRAME_RATE).data
        return VideoAttributes(width, height, rate)


class VideoCodecConfigurationKeys(IntEnum):
    """
    Page 219 / Table 9-26 value for 'Video Codec Type'
    """
    VIDEO_CODEC_TYPE = 1
    VIDEO_CODEC_PARAMETERS = 2
    VIDEO_ATTRIBUTES = 3


class VideoCodecConfiguration:
    """
    Page 219 / Table 9-26 value for 'Video Codec Type'
    """

    def __init__(self,
                 codec_type: VideoCodecType,
                 codec_parameters: VideoCodecParameters,
                 attributes: VideoAttributes):
        self.codec_type = codec_type
        self.codec_parameters = codec_parameters
        self.attributes = attributes

    def to_entry_list(self):
        return tlv8.EntryList([
            tlv8.Entry(VideoCodecConfigurationKeys.VIDEO_CODEC_TYPE, self.codec_type),
            tlv8.Entry(VideoCodecConfigurationKeys.VIDEO_CODEC_PARAMETERS, self.codec_parameters.to_entry_list()),
            tlv8.Entry(VideoCodecConfigurationKeys.VIDEO_ATTRIBUTES, self.attributes.to_entry_list()),
        ])


class SupportedVideoStreamConfiguration:
    """
    Page 219 / Table 9-25
    """
    def __init__(self, config: VideoCodecConfiguration):
        self.config = config

    def to_entry_list(self):
        return tlv8.EntryList([
            tlv8.Entry(1, self.config.to_entry_list())
        ])

    @staticmethod
    def parse(source_bytes):
        data_format = {
            1: tlv8.DataType.BYTES,
        }
        el = tlv8.decode(source_bytes, data_format)
        entry = el.first_by_id(1)
        entry.data = VideoCodecConfiguration.parse(entry.data)
        return el

    @staticmethod
    def from_entry_list(data: tlv8.EntryList):

        config = VideoCodecConfiguration.from_entry_list()
        return SupportedVideoStreamConfiguration(config)


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
