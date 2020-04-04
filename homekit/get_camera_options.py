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
import enum

from homekit.controller import Controller
from homekit.log_support import setup_logging, add_log_arguments
from homekit.model.services import ServicesTypes
from homekit.model.characteristics import CharacteristicsTypes
from homekit.model.characteristics.streaming_status import decoder as streaming_status_decoder
from homekit.model.characteristics.supported_audio_configuration import decoder as supported_audio_configuration_decoder
from homekit.model.characteristics.supported_video_stream_configuration import \
    decoder as supported_video_configuration_decoder
from homekit.model.characteristics.supported_rtp_configuration import decoder as supported_rtp_configuration_decoder

CAMERA_RTP_STREAM_MANAGEMENT_SERVICE = ServicesTypes.get_uuid(ServicesTypes.CAMERA_RTP_STREAM_MANAGEMENT)

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


def pretty_print(entry_list, indent):
    for entry in entry_list:
        if isinstance(entry.data, enum.IntEnum):
            print('{}{}: {}'.format(indent, entry.type_id.name, entry.data.name))
        elif isinstance(entry.data, tlv8.EntryList):
            print('{}{}:'.format(indent, entry.type_id.name))
            pretty_print(entry.data, indent + '\t')
        else:
            print('{}{}: {}'.format(indent, entry.type_id.name, entry.data))


def analyse_streaming_status(in_data: bytes):
    # page 214

    data = streaming_status_decoder(in_data)
    print('\tStreaming Status:')
    pretty_print(data, '\t\t')


def analyse_supported_rtp_configuration(in_data):
    # page 218
    data = supported_rtp_configuration_decoder(in_data)
    print('\tSupported RTP configuration:')
    pretty_print(data, '\t\t')


def analyse_supported_audio_stream_configuration(in_data):
    # page 215
    data = supported_audio_configuration_decoder(in_data)
    print('\tSupported Audio Stream Configuration:')
    pretty_print(data, '\t\t')


def analyse_supported_video_stream_configuration(in_data):
    # page 219
    data = supported_video_configuration_decoder(in_data)
    print('\tSupported Video Stream Configuration:')
    pretty_print(data, '\t\t')


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

    number = 1
    for accessory in data:
        aid = accessory['aid']
        if args.accessory_id and args.accessory_id != aid:
            continue
        for service in accessory['services']:
            s_type = service['type']
            s_iid = service['iid']
            if s_type != CAMERA_RTP_STREAM_MANAGEMENT_SERVICE:
                continue
            print('Management Interface #{}:'.format(number))
            number += 1
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
