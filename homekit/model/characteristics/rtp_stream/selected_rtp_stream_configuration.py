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
import tlv8
from homekit.model.characteristics import CharacteristicsTypes, CharacteristicFormats, CharacteristicPermissions, \
    AbstractCharacteristic

from homekit.model.characteristics.rtp_stream.supported_audio_stream_configuration import AudioCodecType, \
    AudioCodecParameters
from homekit.model.characteristics.rtp_stream.supported_video_stream_configuration import VideoCodecType, \
    VideoCodecParameters, VideoAttributes


class Command(IntEnum):
    """
    Page 205 / Table 9-8 Values for Key Command
    """
    END = 0
    START = 1
    SUSPEND = 2
    RESUME = 3
    RECONFIGURE = 4


class SessionControlKeys(IntEnum):
    """
    Page 205 / Table 9-8
    """
    SESSION_IDENTIFIER = 1
    COMMAND = 2


class SessionControl:
    def __init__(self, session_id, command):
        self.session_id = session_id
        self.command = command

    def to_entry_list(self):
        return tlv8.EntryList([
            tlv8.Entry(SessionControlKeys.SESSION_IDENTIFIER, self.session_id),
            tlv8.Entry(SessionControlKeys.COMMAND, self.command)
        ])


class AudioRtpParametersKey(IntEnum):
    """
    Page 207 / Table 9-12
    """
    PAYLOAD_TYPE = 1
    SSRC_FOR_AUDIO = 2
    MAX_BITRATE = 3
    MIN_RTCP = 4
    COMFORT_NOISE = 6


class AudioRTPParameters:
    """
    Page 207 / Table 9-12
    """

    def __init__(self, payload_type, ssrc_for_audio, max_bitrate, min_rtcp, comfort_noise):
        self.payload_type = payload_type
        self.ssrc_for_audio = ssrc_for_audio
        self.max_bitrate = max_bitrate
        self.min_rtcp = min_rtcp
        self.comfort_noise = comfort_noise

    def to_entry_list(self):
        return tlv8.EntryList([
            tlv8.Entry(AudioRtpParametersKey.PAYLOAD_TYPE, self.payload_type),
            tlv8.Entry(AudioRtpParametersKey.SSRC_FOR_AUDIO, self.ssrc_for_audio),
            tlv8.Entry(AudioRtpParametersKey.MAX_BITRATE, self.max_bitrate),
            tlv8.Entry(AudioRtpParametersKey.MIN_RTCP, self.min_rtcp),
        ])


class SelectedAudioParametersKeys(IntEnum):
    """
    Page 207 / Table 9-11
    """
    SELECTED_AUDIO_CODEC_TYPE = 1
    SELECTED_AUDIO_CODEC_PARAMETERS = 2
    SELECTED_AUDIO_RTP_PARAMETERS = 3
    COMFORT_NOISE = 4


class SelectedAudioParameters:
    """
    Page 207 / Table 9-11
    """

    def __init__(self,
                 selected_audio_codec_type: AudioCodecType,
                 selected_audio_codec_parameters: AudioCodecParameters,
                 selected_audio_rtp_parameters: AudioRTPParameters,
                 comfort_noise: int):
        self.selected_audio_codec_type = selected_audio_codec_type
        self.selected_audio_codec_parameters = selected_audio_codec_parameters
        self.selected_audio_rtp_parameters = selected_audio_rtp_parameters
        self.comfort_noise = comfort_noise

    def to_entry_list(self):
        return tlv8.EntryList([
            tlv8.Entry(SelectedAudioParametersKeys.SELECTED_AUDIO_CODEC_TYPE, self.selected_audio_codec_type),
            tlv8.Entry(SelectedAudioParametersKeys.SELECTED_AUDIO_CODEC_PARAMETERS,
                       self.selected_audio_codec_parameters.to_entry_list()),
            tlv8.Entry(SelectedAudioParametersKeys.SELECTED_AUDIO_RTP_PARAMETERS,
                       self.selected_audio_rtp_parameters.to_entry_list()),
            tlv8.Entry(SelectedAudioParametersKeys.COMFORT_NOISE, self.comfort_noise),
        ])


class VideoRTPParametersKeys(IntEnum):
    """
    Page 206 / Table 9-10
    """
    PAYLOAD_TYPE = 1
    SSRC_FOR_VIDEO = 2
    MAX_BITRATE = 3
    MIN_RTCP = 4
    MAX_MTU = 5


class VideoRTPParameters:
    """
    Page 206 / Table 9-10
    """

    def __init__(self,
                 payload_type,
                 ssrc_for_video,
                 max_bitrate,
                 min_rtcp,
                 max_mtu=1378):
        self.payload_type = payload_type
        self.ssrc_for_video = ssrc_for_video
        self.max_bitrate = max_bitrate
        self.min_rtcp = min_rtcp
        self.max_mtu = max_mtu

    def to_entry_list(self):
        return tlv8.EntryList([
            tlv8.Entry(VideoRTPParametersKeys.PAYLOAD_TYPE, self.payload_type),
            tlv8.Entry(VideoRTPParametersKeys.SSRC_FOR_VIDEO, self.ssrc_for_video),
            tlv8.Entry(VideoRTPParametersKeys.MAX_BITRATE, self.max_bitrate),
            tlv8.Entry(VideoRTPParametersKeys.MIN_RTCP, self.min_rtcp),
        ])


class SelectedVideoParametersKeys(IntEnum):
    """
    Page 205 / Table 9-9
    """
    SELECTED_VIDEO_CODEC_TYPE = 1
    SELECTED_VIDEO_CODEC_PARAMETERS = 2
    SELECTED_VIDEO_ATTRIBUTES = 3
    SELECTED_VIDEO_RTP_PARAMETERS = 4


class SelectedVideoParameters:
    """
    Page 205 / Table 9-9
    """

    def __init__(self,
                 selected_video_codec_type: VideoCodecType,
                 selected_video_codec_parameters: VideoCodecParameters,
                 selected_video_attributes: VideoAttributes,
                 selected_video_rtp_parameters: VideoRTPParameters):
        self.selected_video_codec_type = selected_video_codec_type
        self.selected_video_codec_parameters = selected_video_codec_parameters
        self.selected_video_attributes = selected_video_attributes
        self.selected_video_rtp_parameters = selected_video_rtp_parameters

    def to_entry_list(self):
        return tlv8.EntryList([
            tlv8.Entry(SelectedVideoParametersKeys.SELECTED_VIDEO_CODEC_TYPE, self.selected_video_codec_type),
            tlv8.Entry(SelectedVideoParametersKeys.SELECTED_VIDEO_CODEC_PARAMETERS,
                       self.selected_video_codec_parameters.to_entry_list()),
            tlv8.Entry(SelectedVideoParametersKeys.SELECTED_VIDEO_ATTRIBUTES,
                       self.selected_video_attributes.to_entry_list()),
            tlv8.Entry(SelectedVideoParametersKeys.SELECTED_VIDEO_RTP_PARAMETERS,
                       self.selected_video_rtp_parameters.to_entry_list()),
        ])


class SelectedRtpStreamConfigurationKeys(IntEnum):
    """
    Page 204 / Table 9-7
    """
    SESSION_CONTROL = 1
    SELECTED_VIDEO_PARAMS = 2
    SELECTED_AUDIO_PARAMS = 3


class SelectedRTPStreamConfiguration:
    """
    Page 204 / Table 9-7
    """

    def __init__(self,
                 session_control: SessionControl,
                 selected_video_parameters: SelectedVideoParameters,
                 selected_audio_parameters: SelectedAudioParameters):
        self.session_control = session_control
        self.selected_video_parameters = selected_video_parameters
        self.selected_audio_parameters = selected_audio_parameters

    def to_entry_list(self):
        return tlv8.EntryList([
            tlv8.Entry(SelectedRtpStreamConfigurationKeys.SESSION_CONTROL, self.session_control.to_entry_list()),
            tlv8.Entry(SelectedRtpStreamConfigurationKeys.SELECTED_VIDEO_PARAMS,
                       self.selected_video_parameters.to_entry_list()),
            tlv8.Entry(SelectedRtpStreamConfigurationKeys.SELECTED_AUDIO_PARAMS,
                       self.selected_audio_parameters.to_entry_list()),
        ])


class SelectedRTPStreamConfigurationCharacteristic(AbstractCharacteristic):
    """
    Defined on page 219
    """

    def __init__(self, iid):
        AbstractCharacteristic.__init__(self, iid, CharacteristicsTypes.SELECTED_RTP_STREAM_CONFIGURATION,
                                        CharacteristicFormats.tlv8, SelectedRTPStreamConfiguration)
        self.perms = [CharacteristicPermissions.paired_read, CharacteristicPermissions.paired_write]
        self.description = 'selected streaming video over an RTP session'


class SelectedRTPStreamConfigurationCharacteristicMixin(object):
    def __init__(self, iid):
        self._selectedRTPStreamConfigurationCharacteristic = SelectedRTPStreamConfigurationCharacteristic(iid)
        self.characteristics.append(self._selectedRTPStreamConfigurationCharacteristic)

    def set_selected_rtp_stream_configuration_set_callback(self, callback):
        self._selectedRTPStreamConfigurationCharacteristic.set_set_value_callback(callback)

    def set_selected_rtp_stream_configuration_get_callback(self, callback):
        self._selectedRTPStreamConfigurationCharacteristic.set_get_value_callback(callback)
