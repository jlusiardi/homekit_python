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
import uuid
import tlv8
import time
import base64
import random
import secrets
import tempfile
import subprocess

from homekit.controller import Controller
from homekit.log_support import setup_logging, add_log_arguments
from homekit.model.characteristics import CharacteristicsTypes
from homekit.model.characteristics.setup_endpoints import SetupEndpointsKeys, ControllerAddressKeys, IPVersionValues, \
    SrtpParameterKeys, CameraSRTPCryptoSuiteValues
from homekit.model.characteristics.setup_endpoints import decoder as setup_endpoints_decoder
from homekit.model.characteristics.selected_rtp_stream_configuration import SelectedRtpStreamConfigurationKeys, \
    SessionControlKeys, CommandValues, SelectedVideoParametersKeys, ProfileIdValues, LevelValues, \
    VideoCodecParametersKeys, PacketizationModeValues, VideoAttributesKeys, VideoRTPParametersKeys, \
    SelectedAudioParametersKeys, AudioCodecParametersKeys, BitRateValues, SampleRateValues, RtpTimeValues, \
    AudioRtpParametersKeys, VideoCodecTypeValues, AudioCodecTypeValues

SETUP_ENDPOINTS_CHARACTERISTIC = CharacteristicsTypes.get_uuid(CharacteristicsTypes.SETUP_ENDPOINTS)


def write_sdp_file(accessory_ip, video_port, audio_port):
    content = \
        'c=IN IP4 {a_ip}\n' \
        'm=video {v_port} RTP/AVP 99\n' \
        'a=rtpmap:99 H264/90000\n' \
        'm=audio {a_port} RTP/AVP 110\n' \
        'a=rtpmap:110 Opus/16000/1\n' \
        'a=ptime:20\n' \
        'a=maxptime:20\n'.format(a_ip=accessory_ip, v_port=video_port, a_port=audio_port)
    f = tempfile.NamedTemporaryFile(delete=False)
    f.write(content.encode())
    return f.name


def start_ffplay(sdp_file, master_key, master_salt):
    print(master_key)
    print(master_salt)
    blob = base64.b64encode(master_key + master_salt).decode()
    command = ['ffplay', '-f', 'sdp', sdp_file, '-protocol_whitelist',
               'file,udp,rtp', '-srtp_in_suite',
               'AES_CM_128_HMAC_SHA1_80', '-srtp_in_params', blob]
    print(' '.join(command))
    proc = subprocess.Popen(
        command,
        stdout=sys.stdout,
        stderr=subprocess.STDOUT)
    return proc


def start_ffmpeg(sdp_file, target, master_key, master_salt):
    # '-s:v', '1280x720', '-r', '30',
    #  '-v', 'debug',
    blob = base64.b64encode(master_key + master_salt).decode('ascii')
    command = ['ffmpeg', '-v', 'debug', '-protocol_whitelist', 'file,udp,rtp', '-i',
               sdp_file, '-srtp_in_suite',
               'AES_CM_128_HMAC_SHA1_80', '-srtp_in_params', blob, '-c', 'copy', '-shortest', '-y', target]
    print(' '.join(command))
    proc = subprocess.Popen(
        command,
        stdout=sys.stdout,
        stderr=subprocess.STDOUT)
    return proc


def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit get_resource - retrieve value of snapshot '
                                                 'resource  from paired HomeKit accessories.')
    parser.add_argument('-f', action='store', required=True, dest='file', help='File with the pairing data')
    parser.add_argument('-a', action='store', required=True, dest='alias', help='alias for the pairing')
    parser.add_argument('-A', action='store', dest='accessory_id', help='Accessory id for the camera (optional)')
    parser.add_argument('-W', action='store', default=640, type=int, dest='width', help='Width of the loaded image')
    parser.add_argument('-H', action='store', default=480, type=int, dest='height',
                        help='Height of the loaded image')
    parser.add_argument('-i', action='store', required=True, dest='ip', help='')
    parser.add_argument('-t', action='store', default=1, type=int, dest='time', help='')
    parser.add_argument('-m', action='store', dest='mode', choices=['view', 'save'], default='view')
    parser.add_argument('-o', action='store', dest='output')
    add_log_arguments(parser)
    args = parser.parse_args()
    print('output', args.output)
    if args.mode == 'save' and not args.output:
        print('mode save requires output via -o')
        exit()

    return args


def get_random_port(default_port=None):
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        try:
            if not default_port:
                port = random.randrange(50000, 60000)
                sock.bind(('0.0.0.0', port))
                sock.close()
            else:
                port = default_port
            break
        except Exception:
            pass
    return port


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
        data = pairing.list_accessories_and_characteristics()
        controller.save_data(args.file)
    except Exception as e:
        print(e)
        logging.debug(e, exc_info=True)
        sys.exit(-1)

    aid = 1
    # demo
    if args.alias == 'demo':
        setup_endpoints_iid = 11
        select_rtp_iid = 12
    # circle2
    else:
        setup_endpoints_iid = 21
        select_rtp_iid = 22
        streaming_status_iid = 17

    session_id = uuid.uuid4().bytes

    video_port = get_random_port()
    audio_port = get_random_port()

    video_master_key = secrets.token_bytes(16)
    video_master_salt = secrets.token_bytes(14)

    audio_master_key = video_master_key
    audio_master_salt = video_master_salt

    sdp_file = write_sdp_file(pairing._get_pairing_data()['AccessoryIP'], video_port, audio_port)
    if args.mode == 'view':
        proc = start_ffplay(sdp_file, video_master_key, video_master_salt)
    elif args.mode == 'save':
        proc = start_ffmpeg(sdp_file, args.output, video_master_key, video_master_salt)
    # ==================================================================================================================
    # read status
    p = [(aid, streaming_status_iid)]
    r = base64.b64decode(pairing.get_characteristics(p)[p[0]]['value'])

    # ==================================================================================================================
    # write setup endpoint
    el = tlv8.EntryList()
    el.append(tlv8.Entry(SetupEndpointsKeys.SESSION_ID, session_id))

    controller_address = tlv8.EntryList()
    controller_address.append(tlv8.Entry(ControllerAddressKeys.IP_ADDRESS_VERSION, IPVersionValues.IPV4))
    controller_address.append(tlv8.Entry(ControllerAddressKeys.IP_ADDRESS, args.ip))
    controller_address.append(
        tlv8.Entry(ControllerAddressKeys.VIDEO_RTP_PORT, video_port, tlv8.DataType.UNSIGNED_INTEGER))
    controller_address.append(
        tlv8.Entry(ControllerAddressKeys.AUDIO_RTP_PORT, audio_port, tlv8.DataType.UNSIGNED_INTEGER))
    el.append(tlv8.Entry(SetupEndpointsKeys.ADDRESS, controller_address))

    # SRTP Parameters for Video
    srtp_video = tlv8.EntryList()
    srtp_video.append(tlv8.Entry(SrtpParameterKeys.SRTP_MASTER_KEY, video_master_key))
    srtp_video.append(tlv8.Entry(SrtpParameterKeys.SRTP_MASTER_SALT, video_master_salt))
    srtp_video.append(
        tlv8.Entry(SrtpParameterKeys.SRTP_CRYPTO_SUITE, CameraSRTPCryptoSuiteValues.DISABLED))
    el.append(tlv8.Entry(SetupEndpointsKeys.SRTP_PARAMETERS_FOR_VIDEO, srtp_video))

    # SRTP Parameters for Audio
    srtp_audio = tlv8.EntryList()
    srtp_audio.append(tlv8.Entry(SrtpParameterKeys.SRTP_MASTER_KEY, audio_master_key))
    srtp_audio.append(tlv8.Entry(SrtpParameterKeys.SRTP_MASTER_SALT, audio_master_salt))
    srtp_audio.append(
        tlv8.Entry(SrtpParameterKeys.SRTP_CRYPTO_SUITE, CameraSRTPCryptoSuiteValues.DISABLED))
    el.append(tlv8.Entry(SetupEndpointsKeys.SRTP_PARAMETERS_FOR_AUDIO, srtp_audio))

    # print('\nSetupEndpoints write\n', tlv8.format_string(el))

    val = base64.b64encode(el.encode()).decode('ascii')
    p = [(aid, setup_endpoints_iid, val)]
    # print(p)
    r = pairing.put_characteristics(p)

    # ==================================================================================================================
    # read setup endpoint
    p = [(aid, setup_endpoints_iid)]
    r = pairing.get_characteristics(p)
    val = base64.b64decode(r[(aid, setup_endpoints_iid)]['value'])
    el = setup_endpoints_decoder(val)
    video_ssrc = el.first_by_id(SetupEndpointsKeys.VIDEO_RTP_SSRC).data
    audio_ssrc = el.first_by_id(SetupEndpointsKeys.AUDIO_RTP_SSRC).data

    # ==================================================================================================================
    # write selected stream configuration
    el = tlv8.EntryList()

    session_control = tlv8.EntryList()
    session_control.append(tlv8.Entry(SessionControlKeys.COMMAND, CommandValues.START))
    session_control.append(tlv8.Entry(SessionControlKeys.SESSION_IDENTIFIER, session_id))
    el.append(tlv8.Entry(SelectedRtpStreamConfigurationKeys.SESSION_CONTROL, session_control))

    selected_video_params = tlv8.EntryList()
    selected_video_params.append(
        tlv8.Entry(SelectedVideoParametersKeys.SELECTED_VIDEO_CODEC_TYPE, VideoCodecTypeValues.H264))

    selected_video_codec_params = tlv8.EntryList()
    selected_video_codec_params.append(
        tlv8.Entry(VideoCodecParametersKeys.PROFILE_ID, ProfileIdValues.MAIN_PROFILE))
    selected_video_codec_params.append(tlv8.Entry(VideoCodecParametersKeys.LEVEL, LevelValues.L_4))
    selected_video_codec_params.append(
        tlv8.Entry(VideoCodecParametersKeys.PACKETIZATION_MODE, PacketizationModeValues.NON_INTERLEAVED))
    selected_video_params.append(
        tlv8.Entry(SelectedVideoParametersKeys.SELECTED_VIDEO_CODEC_PARAMETERS, selected_video_codec_params))

    video_parameters = tlv8.EntryList()
    video_parameters.append(tlv8.Entry(VideoAttributesKeys.IMAGE_WIDTH, args.width))
    video_parameters.append(tlv8.Entry(VideoAttributesKeys.IMAGE_HEIGHT, args.height))
    video_parameters.append(tlv8.Entry(VideoAttributesKeys.FRAME_RATE, 30))
    selected_video_params.append(
        tlv8.Entry(SelectedVideoParametersKeys.SELECTED_VIDEO_ATTRIBUTES, video_parameters))

    selected_video_rtp_parameters = tlv8.EntryList()
    selected_video_rtp_parameters.append(tlv8.Entry(VideoRTPParametersKeys.PAYLOAD_TYPE, 99))
    selected_video_rtp_parameters.append(tlv8.Entry(VideoRTPParametersKeys.SSRC_FOR_VIDEO, video_ssrc))
    selected_video_rtp_parameters.append(tlv8.Entry(VideoRTPParametersKeys.MAX_BITRATE, 599))
    selected_video_rtp_parameters.append(tlv8.Entry(VideoRTPParametersKeys.MIN_RTCP, 0.5))
    selected_video_params.append(
        tlv8.Entry(SelectedVideoParametersKeys.SELECTED_VIDEO_RTP_PARAMETERS, selected_video_rtp_parameters))

    el.append(tlv8.Entry(SelectedRtpStreamConfigurationKeys.SELECTED_VIDEO_PARAMS, selected_video_params))

    selected_audio_params = tlv8.EntryList()
    selected_audio_params.append(
        tlv8.Entry(SelectedAudioParametersKeys.SELECTED_AUDIO_CODEC_TYPE, AudioCodecTypeValues.OPUS))

    selected_audio_codec_params = tlv8.EntryList()
    selected_audio_codec_params.append(tlv8.Entry(AudioCodecParametersKeys.AUDIO_CHANNELS, 1))
    selected_audio_codec_params.append(tlv8.Entry(AudioCodecParametersKeys.BIT_RATE, BitRateValues.VARIABLE))
    selected_audio_codec_params.append(tlv8.Entry(AudioCodecParametersKeys.SAMPLE_RATE, SampleRateValues.KHZ_16))
    selected_audio_codec_params.append(tlv8.Entry(AudioCodecParametersKeys.RTP_TIME, RtpTimeValues._20_MS))
    selected_audio_params.append(
        tlv8.Entry(SelectedAudioParametersKeys.SELECTED_AUDIO_CODEC_PARAMETERS, selected_audio_codec_params))

    selected_audio_rtp_parameters = tlv8.EntryList()
    selected_audio_rtp_parameters.append(tlv8.Entry(AudioRtpParametersKeys.PAYLOAD_TYPE, 110))
    selected_audio_rtp_parameters.append(tlv8.Entry(AudioRtpParametersKeys.SSRC_FOR_AUDIO, audio_ssrc))
    selected_audio_rtp_parameters.append(tlv8.Entry(AudioRtpParametersKeys.MAX_BITRATE, b'\x18\x00'))
    selected_audio_rtp_parameters.append(tlv8.Entry(AudioRtpParametersKeys.MIN_RTCP, 5.0))
    selected_audio_rtp_parameters.append(tlv8.Entry(AudioRtpParametersKeys.COMFORT_NOISE, 13))
    selected_audio_params.append(
        tlv8.Entry(SelectedAudioParametersKeys.SELECTED_AUDIO_RTP_PARAMETERS, selected_audio_rtp_parameters))

    selected_audio_params.append(
        tlv8.Entry(SelectedAudioParametersKeys.COMFORT_NOISE, 0))

    el.append(tlv8.Entry(SelectedRtpStreamConfigurationKeys.SELECTED_AUDIO_PARAMS, selected_audio_params))

    val = base64.b64encode(el.encode()).decode('ascii')
    p = [(aid, select_rtp_iid, val)]
    r = pairing.put_characteristics(p)
    print('sent start command', r)

    # ==================================================================================================================
    # stream in progress
    time_done = 0
    while time_done < args.time:
        try:
            time.sleep(1)
            time_done += 1
        except KeyboardInterrupt:
            break

    # ==================================================================================================================
    # write selected stream configuration
    el = tlv8.EntryList()
    session_control = tlv8.EntryList()
    session_control.append(tlv8.Entry(SessionControlKeys.COMMAND, CommandValues.END))
    session_control.append(tlv8.Entry(SessionControlKeys.SESSION_IDENTIFIER, session_id))
    el.append(tlv8.Entry(SelectedRtpStreamConfigurationKeys.SESSION_CONTROL, session_control))
    val = base64.b64encode(el.encode()).decode('ascii')
    p = [(aid, select_rtp_iid, val)]
    r = pairing.put_characteristics(p)

    proc.terminate()
