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
# from homekit.model.characteristics.rtp_stream.supported_audio_stream_configuration import AudioCodecType, \
#     AudioCodecParameters
# from homekit.model.characteristics.rtp_stream.supported_video_stream_configuration import VideoCodecType, \
#     VideoCodecParameters, VideoAttributes


class Command(IntEnum):
    END = 0
    START = 1
    SUSPEND = 2
    RESUME = 3
    RECONFIGURE = 4


class SessionControl:
    #    id = TLVItem(1, bytes)
    #    command = TLVItem(2, Command)
    pass


class AudioRTPParameters:
    #    payload_type = TLVItem(1, int)
    #    ssrc = TLVItem(2, int)
    #    maximum_bitrate = TLVItem(3, int)
    #    comfort_noise_type = TLVItem(5, int)
    pass


class SelectedAudioParameters:
    #    codec_type = TLVItem(1, AudioCodecType)
    #    codec_parameters = TLVItem(2, AudioCodecParameters)
    #    rtp_parameters = TLVItem(3, AudioRTPParameters)
    #    comfort_noise_type = TLVItem(4, int)
    pass


class VideoRTPParameters:
    #    payload_type = TLVItem(1, int)
    #    ssrc = TLVItem(2, int)
    #    maximum_bitrate = TLVItem(3, int)
    #    maximum_mtu = TLVItem(5, int)
    pass


class SelectedVideoParameters:
    #    codec_type = TLVItem(1, VideoCodecType)
    #    codec_parameters = TLVItem(2, VideoCodecParameters)
    #    attributes = TLVItem(3, VideoAttributes)
    #    rtp_parameters = TLVItem(4, VideoRTPParameters)
    pass


class SelectedRTPStreamConfiguration:
    #    session_control = TLVItem(1, SessionControl)
    #    selected_video_parameters = TLVItem(2, SelectedVideoParameters)
    #    selected_audio_parameters = TLVItem(3, SelectedAudioParameters)
    pass


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
