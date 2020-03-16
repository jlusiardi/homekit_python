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
from homekit.model.characteristics.supported_video_stream_configuration import VideoAttributesKeys, \
    VideoCodecParametersKeys, ProfileIdValues, VideoCodecTypeValues, LevelValues, CVOEnabledValue, \
    PacketizationModeValues
from homekit.model.characteristics.supported_audio_configuration import AudioCodecParametersKeys, \
    BitRateValues, SampleRateValues, RtpTimeValues
from homekit.model.characteristics.characteristic_types import CharacteristicsTypes

CHARACTERISTIC_ID = CharacteristicsTypes.get_uuid(CharacteristicsTypes.SELECTED_RTP_STREAM_CONFIGURATION)


class SelectedRtpStreamConfigurationKeys(IntEnum):
    """
    Page 204 / Table 9-7
    """
    SESSION_CONTROL = 1
    SELECTED_VIDEO_PARAMS = 2
    SELECTED_AUDIO_PARAMS = 3


class SessionControlKeys(IntEnum):
    """
    Page 205 / Table 9-8
    """
    SESSION_IDENTIFIER = 1
    COMMAND = 2


class CommandValues(IntEnum):
    """
    Page 205 / Table 9-8 Values for Key Command
    """
    END = 0
    START = 1
    SUSPEND = 2
    RESUME = 3
    RECONFIGURE = 4


class SelectedAudioParametersKeys(IntEnum):
    """
    Page 207 / Table 9-11
    """
    SELECTED_AUDIO_CODEC_TYPE = 1
    SELECTED_AUDIO_CODEC_PARAMETERS = 2
    SELECTED_AUDIO_RTP_PARAMETERS = 3
    COMFORT_NOISE = 4


class SelectedVideoParametersKeys(IntEnum):
    """
    Page 205 / Table 9-9
    """
    SELECTED_VIDEO_CODEC_TYPE = 1
    SELECTED_VIDEO_CODEC_PARAMETERS = 2
    SELECTED_VIDEO_ATTRIBUTES = 3
    SELECTED_VIDEO_RTP_PARAMETERS = 4


class AudioCodecTypeValues(IntEnum):
    """
    Page 207 / Table 9-11 Values for key 'Selected Audio Codec type'
    """
    AAC_ELD = 2
    OPUS = 3
    AMR = 5
    AMR_WB = 6


class VideoRTPParametersKeys(IntEnum):
    """
    Page 206 / Table 9-10
    """
    PAYLOAD_TYPE = 1
    SSRC_FOR_VIDEO = 2
    MAX_BITRATE = 3
    MIN_RTCP = 4
    MAX_MTU = 5


class AudioRtpParametersKeys(IntEnum):
    """
    Page 207 / Table 9-12
    """
    PAYLOAD_TYPE = 1
    SSRC_FOR_AUDIO = 2
    MAX_BITRATE = 3
    MIN_RTCP = 4
    COMFORT_NOISE = 6


def decoder(bytes_data):
    return tlv8.decode(bytes_data, {
        SelectedRtpStreamConfigurationKeys.SESSION_CONTROL: {
            SessionControlKeys.SESSION_IDENTIFIER: tlv8.DataType.BYTES,
            SessionControlKeys.COMMAND: CommandValues,
        },
        SelectedRtpStreamConfigurationKeys.SELECTED_AUDIO_PARAMS: {
            SelectedAudioParametersKeys.SELECTED_AUDIO_CODEC_TYPE: AudioCodecTypeValues,
            SelectedAudioParametersKeys.SELECTED_AUDIO_CODEC_PARAMETERS: {
                AudioCodecParametersKeys.AUDIO_CHANNELS: tlv8.DataType.INTEGER,
                AudioCodecParametersKeys.BIT_RATE: BitRateValues,
                AudioCodecParametersKeys.SAMPLE_RATE: SampleRateValues,
                AudioCodecParametersKeys.RTP_TIME: RtpTimeValues,
            },
            SelectedAudioParametersKeys.SELECTED_AUDIO_RTP_PARAMETERS: {
                AudioRtpParametersKeys.PAYLOAD_TYPE: tlv8.DataType.INTEGER,
                AudioRtpParametersKeys.SSRC_FOR_AUDIO: tlv8.DataType.BYTES,
                AudioRtpParametersKeys.MAX_BITRATE: tlv8.DataType.INTEGER,
                AudioRtpParametersKeys.MIN_RTCP: tlv8.DataType.FLOAT,
                AudioRtpParametersKeys.COMFORT_NOISE: tlv8.DataType.INTEGER,
            },
            SelectedAudioParametersKeys.COMFORT_NOISE: tlv8.DataType.INTEGER,
        },
        SelectedRtpStreamConfigurationKeys.SELECTED_VIDEO_PARAMS: {
            SelectedVideoParametersKeys.SELECTED_VIDEO_CODEC_TYPE: VideoCodecTypeValues,
            SelectedVideoParametersKeys.SELECTED_VIDEO_CODEC_PARAMETERS: {
                VideoCodecParametersKeys.PROFILE_ID: ProfileIdValues,
                VideoCodecParametersKeys.LEVEL: LevelValues,
                VideoCodecParametersKeys.PACKETIZATION_MODE: PacketizationModeValues,
                VideoCodecParametersKeys.CVO_ENABLED: CVOEnabledValue,
            },
            SelectedVideoParametersKeys.SELECTED_VIDEO_ATTRIBUTES: {
                VideoAttributesKeys.IMAGE_WIDTH: tlv8.DataType.INTEGER,
                VideoAttributesKeys.IMAGE_HEIGHT: tlv8.DataType.INTEGER,
                VideoAttributesKeys.FRAME_RATE: tlv8.DataType.INTEGER,
            },
            SelectedVideoParametersKeys.SELECTED_VIDEO_RTP_PARAMETERS: {
                VideoRTPParametersKeys.PAYLOAD_TYPE: tlv8.DataType.INTEGER,
                VideoRTPParametersKeys.SSRC_FOR_VIDEO: tlv8.DataType.BYTES,
                VideoRTPParametersKeys.MAX_BITRATE: tlv8.DataType.INTEGER,
                VideoRTPParametersKeys.MIN_RTCP: tlv8.DataType.FLOAT,
            }
        }
    })
