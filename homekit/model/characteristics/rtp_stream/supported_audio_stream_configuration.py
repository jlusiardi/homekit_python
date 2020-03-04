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


class AudioCodecType(IntEnum):
    """
    Page 207 / Table 9-11 Values for key 'Selected Audio Codec type'
    """
    AAC_ELD = 2
    OPUS = 3
    AMR = 5
    AMR_WB = 6


class BitRate(IntEnum):
    """
    Page 217 / Table 9-21 values for key 'Bit-rate'
    """
    VARIABLE = 0
    CONSTANT = 1


class SampleRate(IntEnum):
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


class AudioCodecParametersKeys(IntEnum):
    """
    Page 217 / Table 9-21
    """
    AUDIO_CHANNELS = 1
    BIT_RATE = 2
    SAMPLE_RATE = 3
    RTP_TIME = 4


class AudioCodecParameters:
    """
    Page 217 / Table 9-21
    """
    def __init__(self, channels,
                 bitrate: BitRate,
                 samplerate: SampleRate,
                 rtp_time: RtpTimeValues = None):
        self.channels = channels
        self.bitrate = bitrate
        self.samplerate = samplerate
        self.rtp_time = rtp_time

    def to_entry_list(self):
        entryList = tlv8.EntryList()
        entryList.append(tlv8.Entry(AudioCodecParametersKeys.AUDIO_CHANNELS, self.channels))
        entryList.append(tlv8.Entry(AudioCodecParametersKeys.BIT_RATE, self.bitrate))
        entryList.append(tlv8.Entry(AudioCodecParametersKeys.SAMPLE_RATE, self.samplerate))
        if self.rtp_time:
            entryList.append(tlv8.Entry(AudioCodecParametersKeys.RTP_TIME, self.rtp_time))
        return entryList

    @staticmethod
    def parse(source_bytes):
        data_format = {
            AudioCodecParametersKeys.AUDIO_CHANNELS: tlv8.DataType.INTEGER,
            AudioCodecParametersKeys.BIT_RATE: BitRate,
            AudioCodecParametersKeys.SAMPLE_RATE: SampleRate,
            AudioCodecParametersKeys.RTP_TIME: RtpTimeValues,
        }
        el = tlv8.decode(source_bytes, data_format)
        return el

    @staticmethod
    def from_entry_list(data: tlv8.EntryList):
        channel = data.first_by_id(AudioCodecParametersKeys.AUDIO_CHANNELS).data
        bitrate = data.first_by_id(AudioCodecParametersKeys.BIT_RATE).data
        samplerate = data.first_by_id(AudioCodecParametersKeys.SAMPLE_RATE).data
        rtp_time = data.first_by_id(AudioCodecParametersKeys.RTP_TIME).data
        return AudioCodecParameters(channel, bitrate, samplerate, rtp_time)


class AudioCodecConfiguration:
    """
    Page 216 / Table 9-19
    """
    def __init__(self,
                 codec_type:AudioCodecType,
                 parameters: AudioCodecParameters):
        self.codec_type = codec_type
        self.parameters = parameters

    def to_entry_list(self):
        entryList = tlv8.EntryList()
        entryList.append(tlv8.Entry(1, self.codec_type))
        entryList.append(tlv8.Entry(2, self.parameters.to_entry_list()))
        return entryList


class SupportedAudioStreamConfiguration:
    def __init__(self, configs, comfort_noise_support):
        self.configs = configs
        self.comfort_noise_support = comfort_noise_support

    def to_entry_list(self):
        entryList = tlv8.EntryList()
        for config in self.configs:
            entryList.append(tlv8.Entry(1, config.to_entry_list(), tlv8.DataType.TLV8))
        entryList.append(tlv8.Entry(2, self.comfort_noise_support))
        return entryList


class SupportedAudioStreamConfigurationCharacteristic(AbstractCharacteristic):
    """
    Defined on page 215
    """

    def __init__(self, iid, value):
        AbstractCharacteristic.__init__(self, iid, CharacteristicsTypes.SUPPORTED_AUDIO_CONFIGURATION,
                                        CharacteristicFormats.tlv8, SupportedAudioStreamConfiguration)
        self.perms = [CharacteristicPermissions.paired_read]
        self.description = 'parameters supported for streaming audio over an RTP session'
        self.value = value
