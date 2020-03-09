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
from homekit.model.characteristics import CharacteristicsTypes, CharacteristicPermissions, AbstractTlv8Characteristic, \
    AbstractTlv8CharacteristicValue


class ComfortNoiseSupport(IntEnum):
    """
    Page 215 / Table 9-18 Values for key 'Comfort Noise support'
    """
    NO_COMFORT_NOISE = 0
    COMFORT_NOISE = 1


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


class AudioCodecParameters(AbstractTlv8CharacteristicValue):
    """
    Page 217 / Table 9-21
    """

    def __init__(self, channels,
                 bit_rate: BitRate,
                 sample_rate: SampleRate,
                 rtp_time: RtpTimeValues = None):
        """
        :param rtp_time: This is the optional value of the length represented in the packet. Only available when used
            in the context of "Selected Audio Codec Parameters TLV".
        """
        self.channels = channels
        self.bit_rate = bit_rate
        self.sample_rate = sample_rate
        self.rtp_time = rtp_time

    def to_bytes(self) -> bytes:
        entry_list = tlv8.EntryList()
        entry_list.append(tlv8.Entry(AudioCodecParametersKeys.AUDIO_CHANNELS, self.channels))
        entry_list.append(tlv8.Entry(AudioCodecParametersKeys.BIT_RATE, self.bit_rate))
        entry_list.append(tlv8.Entry(AudioCodecParametersKeys.SAMPLE_RATE, self.sample_rate))
        if self.rtp_time:
            entry_list.append(tlv8.Entry(AudioCodecParametersKeys.RTP_TIME, self.rtp_time))
        return entry_list.encode()

    @staticmethod
    def from_bytes(data: bytes):
        data_format = {
            AudioCodecParametersKeys.AUDIO_CHANNELS: tlv8.DataType.INTEGER,
            AudioCodecParametersKeys.BIT_RATE: BitRate,
            AudioCodecParametersKeys.SAMPLE_RATE: SampleRate,
            AudioCodecParametersKeys.RTP_TIME: RtpTimeValues,
        }
        el = tlv8.decode(data, data_format)
        channel = el.first_by_id(AudioCodecParametersKeys.AUDIO_CHANNELS).data
        bit_rate = el.first_by_id(AudioCodecParametersKeys.BIT_RATE).data
        sample_rate = el.first_by_id(AudioCodecParametersKeys.SAMPLE_RATE).data
        rtp_time = el.first_by_id(AudioCodecParametersKeys.RTP_TIME)
        if rtp_time:
            rtp_time = rtp_time.data
        return AudioCodecParameters(channel, bit_rate, sample_rate, rtp_time)


class AudioCodecConfigurationKeys(IntEnum):
    """
    Page 215 / Table 9-18
    """
    CODEC_TYPE = 1
    AUDIO_CODEC_PARAMETERS = 2


class AudioCodecConfiguration(AbstractTlv8CharacteristicValue):
    """
    Page 216 / Table 9-19
    """

    def __init__(self,
                 codec_type: AudioCodecType,
                 parameters: AudioCodecParameters):
        self.codec_type = codec_type
        self.parameters = parameters

    def to_bytes(self) -> bytes:
        entry_list = tlv8.EntryList()
        entry_list.append(tlv8.Entry(AudioCodecConfigurationKeys.CODEC_TYPE, self.codec_type))
        entry_list.append(
            tlv8.Entry(AudioCodecConfigurationKeys.AUDIO_CODEC_PARAMETERS, self.parameters.to_bytes()))
        return entry_list.encode()

    @staticmethod
    def from_bytes(data: bytes):
        el = tlv8.decode(data, {
            AudioCodecConfigurationKeys.CODEC_TYPE: AudioCodecType,
            AudioCodecConfigurationKeys.AUDIO_CODEC_PARAMETERS: tlv8.DataType.BYTES
        })
        codec_type = el.first_by_id(AudioCodecConfigurationKeys.CODEC_TYPE).data
        parameters = AudioCodecParameters.from_bytes(
            el.first_by_id(AudioCodecConfigurationKeys.AUDIO_CODEC_PARAMETERS).data)
        return __class__(codec_type, parameters)


class SupportedAudioStreamConfigurationKeys(IntEnum):
    """
    Page 215 / Table 9-18
    """
    AUDIO_CODEC_CONFIGURATION = 1
    COMFORT_NOISE_SUPPORT = 2


class SupportedAudioStreamConfiguration(AbstractTlv8CharacteristicValue):
    """
    Page 215 / Table 9-18
    """

    def __init__(self,
                 config,
                 comfort_noise_support: ComfortNoiseSupport):
        self.config = config
        self.comfort_noise_support = comfort_noise_support

    def to_bytes(self) -> bytes:
        entry_list = tlv8.EntryList()
        entry_list.append(
            tlv8.Entry(SupportedAudioStreamConfigurationKeys.AUDIO_CODEC_CONFIGURATION, self.config.to_bytes()))
        entry_list.append(
            tlv8.Entry(SupportedAudioStreamConfigurationKeys.COMFORT_NOISE_SUPPORT, self.comfort_noise_support))
        return entry_list.encode()

    @staticmethod
    def from_bytes(data: bytes):
        el = tlv8.decode(data, {
            SupportedAudioStreamConfigurationKeys.AUDIO_CODEC_CONFIGURATION: tlv8.DataType.BYTES,
            SupportedAudioStreamConfigurationKeys.COMFORT_NOISE_SUPPORT: ComfortNoiseSupport
        })
        config = AudioCodecConfiguration.from_bytes(
            el.first_by_id(SupportedAudioStreamConfigurationKeys.AUDIO_CODEC_CONFIGURATION).data)
        comfort_noise = el.first_by_id(SupportedAudioStreamConfigurationKeys.COMFORT_NOISE_SUPPORT).data
        return __class__(config, comfort_noise)


class SupportedAudioStreamConfigurationCharacteristic(AbstractTlv8Characteristic):
    """
    Defined on page 215
    """

    def __init__(self, iid, value):
        AbstractTlv8Characteristic.__init__(self, iid, value, CharacteristicsTypes.SUPPORTED_AUDIO_CONFIGURATION)
        self.perms = [CharacteristicPermissions.paired_read]
        self.description = 'parameters supported for streaming audio over an RTP session'
        self.value = value


class SupportedAudioStreamConfigurationCharacteristicMixin(object):
    def __init__(self, iid):
        self._supportedAudioStreamConfigurationCharacteristic = SupportedAudioStreamConfigurationCharacteristic(iid)
        self.characteristics.append(self._supportedAudioStreamConfigurationCharacteristic)

    def set_streaming_status_get_callback(self, callback):
        self._supportedAudioStreamConfigurationCharacteristic.set_get_value_callback(callback)
