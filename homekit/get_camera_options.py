# !/usr/bin/env python3

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

import argparse
import sys
import logging
import base64
import tlv8
from enum import IntEnum

from homekit.controller import Controller
from homekit.log_support import setup_logging, add_log_arguments
from homekit.model.characteristics import CharacteristicsTypes
from homekit.model.characteristics.rtp_stream.supported_rtp_configuration import CameraSRTPCryptoSuite, SupportedRtpConfigurationKeys
from homekit.model.characteristics.rtp_stream.streaming_status import StreamingStatusValue, StreamingStatusKey


STREAMING_STATUS_CHARACTERISTIC = CharacteristicsTypes.get_uuid(CharacteristicsTypes.STREAMING_STATUS)
SUPPORTED_AUDIO_STREAM_CONFIGURATION_CHARACTERISTIC = \
    CharacteristicsTypes.get_uuid(CharacteristicsTypes.SUPPORTED_AUDIO_CONFIGURATION)
SUPPORTED_VIDEO_STREAM_CONFIGURATION_CHARACTERISTIC = \
    CharacteristicsTypes.get_uuid(CharacteristicsTypes.SUPPORTED_VIDEO_STREAM_CONFIGURATION)
SUPPORTED_RTP_CONFIGURATION_CHARACTERISTIC = \
    CharacteristicsTypes.get_uuid(CharacteristicsTypes.SUPPORTED_RTP_CONFIGURATION)


def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit get_resource - retrieve value of snapshot '
                                                 'resource  from paired HomeKit accessories.')
    parser.add_argument('-f', action='store', required=True, dest='file', help='File with the pairing data')
    parser.add_argument('-a', action='store', required=True, dest='alias', help='alias for the pairing')
    parser.add_argument('-A', action='store', dest='accessory_id', help='Accessory id for the camera (optional)')
    add_log_arguments(parser)
    return parser.parse_args()


def analyse_streaming_status(in_data):
    # page 214

    data = tlv8.decode(in_data, {
        StreamingStatusKey.STATUS: StreamingStatusValue,
    })
    print('Streaming Status', tlv8.format_string(data))


def analyse_supported_rtp_configuration(in_data):
    # 218
    data = tlv8.decode(in_data, {
        SupportedRtpConfigurationKeys.SRTP_CRYPTO_SUITE: CameraSRTPCryptoSuite,
    })
    print('Supported RTP configuration', tlv8.format_string(data))


def analyse_supported_audio_stream_configuration(in_data):
    # page 215
    class SupportedAudioStreamConfigurationKey(IntEnum):
        AUDIO_CODEC_CONFIGURATION = 1
        COMFORT_NOISE_SUPPORT = 2

    class AudioCodecsKey(IntEnum):
        CODEC_TYPE = 1
        AUDIO_CODEC_PARAMETERS = 2

    class AudioCodecParameterKey(IntEnum):
        AUDIO_CHANNELS = 1
        BIT_RATE = 2
        SAMPLE_RATE = 3
        RTP_TIME = 4

    class ComfortNoiseSupportValue(IntEnum):
        NOT_SUPPORTED = 0
        SUPPORTED = 1

    class CodecTypeValue(IntEnum):
        AAC_ELD = 2
        OPUS = 3
        AMR = 5
        AMR_WB = 6

    class BitRateValue(IntEnum):
        VARIABLE_BIT_RATE = 0
        CONSTANT_BIT_RATE = 1

    class SampleRateValue(IntEnum):
        KHZ_8 = 0
        KHZ_16 = 1
        KHZ_24 = 2

    data = tlv8.decode(in_data, {
        SupportedAudioStreamConfigurationKey.AUDIO_CODEC_CONFIGURATION: {
            AudioCodecsKey.CODEC_TYPE: CodecTypeValue,
            AudioCodecsKey.AUDIO_CODEC_PARAMETERS: {
                AudioCodecParameterKey.AUDIO_CHANNELS: tlv8.DataType.INTEGER,
                AudioCodecParameterKey.BIT_RATE: BitRateValue,
                AudioCodecParameterKey.SAMPLE_RATE: SampleRateValue,
                AudioCodecParameterKey.RTP_TIME: tlv8.DataType.INTEGER,
            },
        },
        SupportedAudioStreamConfigurationKey.COMFORT_NOISE_SUPPORT: ComfortNoiseSupportValue,
    })
    print('Supported Audio Stream Configuration', tlv8.format_string(data))


def analyse_supported_video_stream_configuration(in_data):
    # page 219
    class SupportedVideoStreamConfigurationKey(IntEnum):
        VIDEO_CODEC_CONFIGURATION = 1

    class VideoCodecConfiguration(IntEnum):
        VIDEO_CODEC_TYPE = 1
        VIDEO_CODEC_PARAMETERS = 2
        VIDEO_CODEC_ATTRIBUTES = 3

    class VideoCodecType(IntEnum):
        H_264 = 0

    class VideoCodecParameters(IntEnum):
        PROFILE_ID = 1
        LEVEL = 2
        PACKETIZATION_MODE = 3
        CVO_ENABLED = 4
        CVO_ID = 5

    class ProfileID(IntEnum):
        CONSTRAINT_BASELINE_PROFILE = 0
        MAIN_PROFILE = 1
        HIGH_PROFILE = 2

    class Level(IntEnum):
        LEVEL_3_1 = 0
        LEVEL_3_2 = 1
        LEVEL_4 = 2

    class PacketizationMode(IntEnum):
        NON_INTERLEAVED_MODE = 0

    class CvoEnabled(IntEnum):
        CVO_NOT_SUPPORTED = 0
        CVO_SUPPORTED = 1

    class VideoAttributes(IntEnum):
        IMAGE_WIDTH = 1
        IMAGE_HEIGHT = 2
        FRAME_RATE = 3

    data = tlv8.decode(in_data, {
        SupportedVideoStreamConfigurationKey.VIDEO_CODEC_CONFIGURATION: {
            VideoCodecConfiguration.VIDEO_CODEC_TYPE: VideoCodecType,
            VideoCodecConfiguration.VIDEO_CODEC_PARAMETERS: {
                VideoCodecParameters.PROFILE_ID: ProfileID,
                VideoCodecParameters.LEVEL: Level,
                VideoCodecParameters.PACKETIZATION_MODE: PacketizationMode,
                VideoCodecParameters.CVO_ENABLED: CvoEnabled,
                VideoCodecParameters.CVO_ID: tlv8.DataType.INTEGER,
            },
            VideoCodecConfiguration.VIDEO_CODEC_ATTRIBUTES: {
                VideoAttributes.IMAGE_WIDTH: tlv8.DataType.INTEGER,
                VideoAttributes.IMAGE_HEIGHT: tlv8.DataType.INTEGER,
                VideoAttributes.FRAME_RATE: tlv8.DataType.INTEGER,
            }
        }
    })
    print('Supported Video Stream Configuration', tlv8.format_string(data))


if __name__ == '__main__':
    args = setup_args_parser()

    setup_logging(args.loglevel)

    controller = Controller()
    controller.load_data(args.file)
    if args.alias not in controller.get_pairings():
        print('"{a}" is no known alias'.format(a=args.alias))
        sys.exit(-1)

    try:
        pairing = controller.get_pairings()[args.alias]
        data = pairing.list_accessories_and_characteristics()
        controller.save_data(args.file)
    except Exception as e:
        print(e)
        logging.debug(e, exc_info=True)
        sys.exit(-1)

    for accessory in data:
        aid = accessory['aid']
        if args.accessory_id and args.accessory_id != aid:
            continue
        for service in accessory['services']:
            s_type = service['type']
            s_iid = service['iid']
            for characteristic in service['characteristics']:
                c_type = characteristic['type']
                if c_type == STREAMING_STATUS_CHARACTERISTIC:
                    value = base64.b64decode(characteristic['value'])
                    analyse_streaming_status(value)
                if c_type == SUPPORTED_AUDIO_STREAM_CONFIGURATION_CHARACTERISTIC:
                    value = base64.b64decode(characteristic['value'])
                    analyse_supported_audio_stream_configuration(value)
                if c_type == SUPPORTED_VIDEO_STREAM_CONFIGURATION_CHARACTERISTIC:
                    value = base64.b64decode(characteristic['value'])
                    analyse_supported_video_stream_configuration(value)
                if c_type == SUPPORTED_RTP_CONFIGURATION_CHARACTERISTIC:
                    value = base64.b64decode(characteristic['value'])
                    analyse_supported_rtp_configuration(value)
