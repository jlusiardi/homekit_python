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


class AudioCodecType(IntEnum):
    AAC_ELD = 2
    OPUS = 3
    AMR = 5
    AMR_WB = 6


class BitRate(IntEnum):
    VARIABLE = 0
    CONSTANT = 1


class SampleRate(IntEnum):
    KHZ_8 = 0
    KHZ_16 = 1
    KHZ_24 = 2


class AudioCodecParameters:
    channels = TLVItem(1, int)
    bitrate = TLVItem(2, BitRate)
    samplerate = TLVItem(3, SampleRate)
    time = TLVItem(4, int)

    def __init__(self, channels, bitrate, samplerate):
        self.channels = channels
        self.bitrate = bitrate
        self.samplerate = samplerate


class AudioCodecConfiguration:
    codec_type = TLVItem(1, AudioCodecType)
    parameters = TLVItem(2, AudioCodecParameters)

    def __init__(self, codec_type, parameters):
        self.codec_type = codec_type
        self.parameters = parameters


class SupportedAudioStreamConfiguration:
    config = TLVItem(1, AudioCodecConfiguration)
    comfort_noise_support = TLVItem(2, int)

    def __init__(self, config, comfort_noise_support):
        self.config = config
        self.comfort_noise_support = comfort_noise_support


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
