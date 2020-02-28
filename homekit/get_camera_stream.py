# !/usr/bin/env python3

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

import argparse
import sys
import logging
import uuid
import tlv8
import base64

from homekit.controller import Controller
from homekit.log_support import setup_logging, add_log_arguments
from homekit.model.characteristics import CharacteristicsTypes
from homekit.model.characteristics.rtp_stream.setup_endpoints import SRTPParameters, SetupEndpointsKeys, Address, \
    SetupEndpointsResponse
from homekit.model.characteristics.rtp_stream.supported_rtp_configuration import CameraSRTPCryptoSuite
from homekit.model.characteristics.rtp_stream.supported_video_stream_configuration import VideoAttributes, \
    VideoCodecType, VideoCodecParameters, H264Level, H264Profile, PacketizationMode, CVOEnabled
from homekit.model.characteristics.rtp_stream.supported_audio_stream_configuration import AudioCodecType, \
    AudioCodecParameters, BitRate, SampleRate
from homekit.model.characteristics.rtp_stream.selected_rtp_stream_configuration import SelectedRTPStreamConfiguration, \
    SessionControl, Command, SelectedVideoParameters, SelectedAudioParameters, AudioRTPParameters, VideoRTPParameters

SETUP_ENDPOINTS_CHARACTERISTIC = CharacteristicsTypes.get_uuid(CharacteristicsTypes.SETUP_ENDPOINTS)


def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit get_resource - retrieve value of snapshot '
                                                 'resource  from paired HomeKit accessories.')
    parser.add_argument('-f', action='store', required=True, dest='file', help='File with the pairing data')
    parser.add_argument('-a', action='store', required=True, dest='alias', help='alias for the pairing')
    parser.add_argument('-A', action='store', dest='accessory_id', help='Accessory id for the camera (optional)')
    parser.add_argument('-W', action='store', default=640, type=int, dest='width', help='Width of the loaded image')
    parser.add_argument('-H', action='store', default=480, type=int, dest='height', help='Height of the loaded image')
    add_log_arguments(parser)
    return parser.parse_args()


if __name__ == '__main__':
    args = setup_args_parser()

    setup_logging(args.loglevel)

    controller = Controller()
    controller.load_data(args.file)
    if args.alias not in controller.get_pairings():
        print('"{a}" is no known alias'.format(a=args.alias))
        sys.exit(-1)

    pairing = controller.get_pairings()[args.alias]

    try:
        pairing = controller.get_pairings()[args.alias]
        data = pairing.list_accessories_and_characteristics()
        controller.save_data(args.file)
    except Exception as e:
        print(e)
        logging.debug(e, exc_info=True)
        sys.exit(-1)

    aid = 1
    # demo
    setup_endpoints_iid = 11
    select_rtp_iid = 12
    # circle2
    setup_endpoints_iid = 21
    select_rtp_iid = 22

    session_id = uuid.uuid4().bytes
    # write setup endpoint
    el = tlv8.EntryList()
    el.append(tlv8.Entry(SetupEndpointsKeys.SESSION_ID, session_id))

    controller_address = Address('192.168.178.32', 32100, 32101)
    el.append(tlv8.Entry(SetupEndpointsKeys.CONTROLLER_ADDRESS, controller_address.to_entry_list()))
    # SRTP Parameters for Video
    srtp_video = SRTPParameters(CameraSRTPCryptoSuite.DISABLED)
    el.append(tlv8.Entry(SetupEndpointsKeys.SRTP_PARAMETERS_FOR_VIDEO, srtp_video.to_entry_list()))

    # SRTP Parameters for Audio
    srtp_audio = SRTPParameters(CameraSRTPCryptoSuite.DISABLED)
    el.append(tlv8.Entry(SetupEndpointsKeys.SRTP_PARAMETERS_FOR_AUDIO, srtp_audio.to_entry_list()))

    print('\nSetupEndpoints write\n', tlv8.format_string(el))

    val = base64.b64encode(el.encode()).decode('ascii')
    p = [(aid, setup_endpoints_iid, val)]
    r = pairing.put_characteristics(p)
    # print(r)

    # read setup endpoint
    p = [(aid, setup_endpoints_iid)]
    r = pairing.get_characteristics(p)
    # print(r)
    val = base64.b64decode(r[(aid, setup_endpoints_iid)]['value'])
    val = SetupEndpointsResponse.parse(val)

    print('\nSetupEndpoints read\n', tlv8.format_string(val))
    video_ssrc = val.first_by_id(6).data
    audio_ssrc = val.first_by_id(7).data

    # write selected stream configuration
    sc = SessionControl(session_id, Command.START)
    svp = SelectedVideoParameters(
        VideoCodecType.H264,
        VideoCodecParameters(H264Profile.MAIN_PROFILE, H264Level.L_4, PacketizationMode.NON_INTERLEAVED,
                             CVOEnabled.NOT_SUPPORTED),
        VideoAttributes(1280, 720, 30),
        VideoRTPParameters(VideoCodecType.H264, video_ssrc, 1024, 0.5)
    )
    sap = SelectedAudioParameters(
        AudioCodecType.OPUS,
        AudioCodecParameters(1, BitRate.VARIABLE, SampleRate.KHZ_16, rtp_time=30),
        AudioRTPParameters(0, audio_ssrc, 32, 10.0, 0),
        0
    )
    srsc = SelectedRTPStreamConfiguration(sc, svp, sap)
    el = srsc.to_entry_list()
    print('\nSelect RTP Stream Config write\n', tlv8.format_string(el))
    print(el.encode().hex())
    val = base64.b64encode(el.encode()).decode('ascii')
    p = [(aid, select_rtp_iid, val)]
    r = pairing.put_characteristics(p)
    print(r)

    # stream in progress
