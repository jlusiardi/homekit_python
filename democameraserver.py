#!/usr/bin/env python3

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

from homekit import AccessoryServer
from homekit.model import CameraAccessory, ManagedRTPStreamService, MicrophoneService
from homekit.model.characteristics.rtp_stream.setup_endpoints import Address, IPVersion
from homekit.model.characteristics.rtp_stream.supported_audio_stream_configuration import \
    SupportedAudioStreamConfiguration, AudioCodecConfiguration, AudioCodecType, AudioCodecParameters, BitRate, \
    SampleRate
from homekit.model.characteristics.rtp_stream.supported_rtp_configuration import SupportedRTPConfiguration, \
    CameraSRTPCryptoSuite
from homekit.model.characteristics.rtp_stream.supported_video_stream_configuration import \
    SupportedVideoStreamConfiguration, VideoCodecConfiguration, VideoCodecParameters, H264Profile, H264Level, \
    VideoAttributes

import subprocess
import base64
from PIL import Image, ImageDraw
import logging
import datetime
import argparse
import os.path

def get_image_snapshot(format_data):
    img = Image.new('RGB', (format_data['image-width'],format_data['image-height']), '#FFFFFF')
    d = ImageDraw.Draw(img)
    d.text((10,60), datetime.datetime.now().isoformat(), fill=(0,0,0))
    d.text((10,100), str(format_data), fill=(0,0,0))
    img.save('foo.jpg','JPEG')
    b2 = open('foo.jpg', 'rb').read()
    return b2

def setup_args_parser():
    parser = argparse.ArgumentParser(description='HomeKit demo server')
    parser.add_argument('-f', action='store', required=False, dest='file', default='./demoserver.json',
                        help='File with the config data (defaults to ./demoserver.json)')
    parser.add_argument('-c', action='store', required=True, dest='camera')
    parser.add_argument('-d', action='store', required=True, dest='driver')
    return parser.parse_args()

if __name__ == '__main__':
    args = setup_args_parser()
    config_file = os.path.expanduser(args.file)
    logger = logging.getLogger('accessory')
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s %(filename)s:%(lineno)04d %(levelname)s %(message)s'))
    logger.addHandler(ch)
    logger.info('starting')

    try:
        httpd = AccessoryServer('demoserver.json')

        accessory = CameraAccessory('Testkamera', 'wiomoc', 'Demoserver', '0001', '0.1')

        accessory.set_get_image_snapshot_callback(get_image_snapshot)

        class StreamHandler:
            def __init__(self, controller_address, srtp_params_video, **_):
                self.srtp_params_video = srtp_params_video
                self.controller_address = controller_address
                self.ffmpeg_process = None

            def on_start(self, attrs):
                self.ffmpeg_process = subprocess.Popen(
                    ['ffmpeg', '-re',
                     # read input at native frame rate
                     '-re',
                     # chose input driver
                     '-f', args.driver,  # linux
                     #                     '-f', 'avfoundation', # mac
                     # set frame rate
                     #                     '-r', '30.000030',
                     # chose proper input device aka camera
                     '-i', args.camera, #'/dev/video0',  # first device on linux
                     #                     '-i', 'Integrierte iSight-Kamera',  # mac device may also be 'FaceTime HD-Kamera (integriert)'
                     #                     '-threads', '0',
                     # set the video codec to H.264 (Spec R2, chapter 11.8, page 245)
                     '-vcodec', 'libx264',
                     # no audio
                     #                     '-an',
                     '-pix_fmt', 'yuv420p',
                     # set frame rate
                     '-r', str(attrs.attributes.frame_rate),
                     '-f', 'rawvideo',
                     '-tune', 'zerolatency',
                     '-vf', f'scale={attrs.attributes.width}:{attrs.attributes.height}',
                     # set video bandwidth
                     '-b:v', '300k',
                     # set size of buffer
                     '-bufsize', '300k',
                     '-payload_type', '99',
                     '-ssrc', '32',
                     '-f', 'rtp',
                     '-srtp_out_suite', 'AES_CM_128_HMAC_SHA1_80',
                     '-srtp_out_params', base64.b64encode(
                        self.srtp_params_video.master_key + self.srtp_params_video.master_salt).decode('ascii'),
                     f'srtp://{self.controller_address.ip_address}:{self.controller_address.video_rtp_port}'
                     f'?rtcpport={self.controller_address.video_rtp_port}'
                     f'&localrtcpport={self.controller_address.video_rtp_port}'
                     # packet size for IPv4 (1378 bytes) / IPv6 (1228) as defined by spec r2 chapter 11.8.1 page 246
                     '&pkt_size=1378'
                     ])

            def on_end(self):
                if self.ffmpeg_process is not None:
                    self.ffmpeg_process.terminate()

            def get_ssrc(self):
                return (32, 32)

            def get_address(self):
                return Address(IPVersion.IPV4, httpd.data.ip, self.controller_address.video_rtp_port,
                               self.controller_address.audio_rtp_port)


        stream_service = ManagedRTPStreamService(
            StreamHandler,
            SupportedRTPConfiguration(
                [
                    CameraSRTPCryptoSuite.AES_CM_128_HMAC_SHA1_80,
                ]),
            SupportedVideoStreamConfiguration(
                VideoCodecConfiguration(
                    VideoCodecParameters(
                        [H264Profile.CONSTRAINED_BASELINE_PROFILE, H264Profile.MAIN_PROFILE, H264Profile.HIGH_PROFILE],
                        [H264Level.L_3_1, H264Level.L_3_2, H264Level.L_4]
                    ), [
                        VideoAttributes(1920, 1080, 30),
                        VideoAttributes(320, 240, 15),
                        VideoAttributes(1280, 960, 30),
                        VideoAttributes(1280, 720, 30),
                        VideoAttributes(1280, 768, 30),
                        VideoAttributes(640, 480, 30),
                        VideoAttributes(640, 360, 30)
                    ])),
            SupportedAudioStreamConfiguration([
                AudioCodecConfiguration(AudioCodecType.OPUS,
                                        AudioCodecParameters(1, BitRate.VARIABLE, SampleRate.KHZ_24)),
                AudioCodecConfiguration(AudioCodecType.AAC_ELD,
                                        AudioCodecParameters(1, BitRate.VARIABLE, SampleRate.KHZ_16))
            ], 0))
        accessory.services.append(stream_service)
        microphone_service = MicrophoneService()
        accessory.services.append(microphone_service)
        httpd.accessories.add_accessory(accessory)

        httpd.publish_device()
        print('published device and start serving')
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('unpublish device')
        httpd.unpublish_device()
