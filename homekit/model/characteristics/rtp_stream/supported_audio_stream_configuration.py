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
    def __init__(self, channels, bitrate, samplerate, rtp_time=None):
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


class AudioCodecConfiguration:
    #    codec_type = TLVItem(1, AudioCodecType)
    #    parameters = TLVItem(2, AudioCodecParameters)

    def __init__(self, codec_type, parameters):
        self.codec_type = codec_type
        self.parameters = parameters

    def to_entry_list(self):
        entryList = tlv8.EntryList()
        entryList.append(tlv8.Entry(1, self.codec_type))
        print(self.parameters)
        return entryList


class SupportedAudioStreamConfiguration:
    #    config = TLVItem(1, AudioCodecConfiguration)
    #    comfort_noise_support = TLVItem(2, int)

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
